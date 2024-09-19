import asyncio
import logging
import warnings

from hexbytes import HexBytes
from web3 import Web3

from item.evm.ac import ABI
from item.evm.ps import FundsFlowSubgraph, Timestamp, Input
from item.evm.tx import Receipt
from settings import HEADER
from spider.evm.ac import TxListSpider, ABISpider
from spider.evm.blk import BlockSpider
from spider.evm.tx import TransactionSpider, TraceSpider, ReceiptSpider
from spider.meta import Spider
from utils.conf import Vm, Net, Module, Mode
from utils.req import Request, Headers, Result
from utils.web3 import parse_hexbytes_dict


class FundsFlowSubgraphSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.PS, Mode.FFS)
        self.trans_spider = TransactionSpider(vm, net)
        self.txlist_spider = TxListSpider(vm, net)

    async def parse(self, **kwargs):
        key = kwargs.get("id")
        hash = kwargs.get("hash")
        out = kwargs.get("out")

        trans_queue = await self.trans_spider.crawl(params=[{
            'hash': hash,
            'out': out
        }])
        trans = trans_queue[0]
        if len(trans.item) == 0:
            return Result(key=key, item={})

        res_arr = []
        for a in [trans.item.get("from_"), trans.item.get("to_")]:
            block_number = trans.item.get("block_number")
            txlist_queue = await self.txlist_spider.crawl(params=[{
                'address': a,
                'start_blk': block_number, 'end_blk': block_number,
                'out': out
            }])
            res_arr.append(txlist_queue[0])
        from_res, to_res = res_arr[0], res_arr[1]

        if len(from_res.item) == 0 and len(to_res.item) == 0:
            return Result(key=key, item={})

        nodes, edges = [], []
        for e in from_res.item.get('array', []) + to_res.item.get('array', []):
            if e.get('hash', '').lower() != hash.lower():
                continue

            nodes.append(e.get('from_'))
            nodes.append(e.get('to_'))
            edges.append({
                'from': e.get('from_'),
                'to': e.get('to_'),
                'attributes': {
                    k: v for k, v in e.items()
                    if k not in ['hash', 'from_', 'to_']
                }
            })

        return Result(
            key=key, item=FundsFlowSubgraph().map({
                'hash': hash,
                'edges': edges,
                'nodes': list(set(nodes))
            }) if len(nodes) != 0 else {}
        )


class TimestampParser(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.PS, Mode.TS)
        self.blk_spider = BlockSpider(vm, net)
        self.trans_spider = TransactionSpider(vm, net)

    async def parse(self, **kwargs):
        key = kwargs.get("id")
        hash = kwargs.get("hash")
        out = kwargs.get("out")

        trans_queue = await self.trans_spider.crawl(params=[{
            'hash': hash,
            'out': out
        }])
        trans = trans_queue[0]
        if len(trans.item) == 0:
            return Result(key=key, item={})

        blk_hash_arr = trans.item.dict().get("block_hash")
        block_queue = await self.blk_spider.crawl(list(blk_hash_arr), Mode.BLOCK, out)
        block = block_queue[0]
        if len(block.item) == 0:
            return Result(key=key, item={})

        return Result(
            key=key, item=Timestamp().map({
                'hash': hash,
                'timestamp': block.get('timestamp'),
                'block_number': trans.get('block_number')
            }).dict()
        )


def get_impl_address(address: str, trace: dict):
    trace_arr = trace.get('array', [])
    try:
        address = next(
            t.get('action', {}).get('to_')
            for t in trace_arr
            if (
                    t.get('action', {}).get('call_type').lower() == "delegatecall"
                    and t.get('action', {}).get('from_').lower() == address.lower()
            )
        )
    except (StopIteration, Exception):
        pass
    return address


class InputParser(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.PS, Mode.IN)
        self.w3 = Web3(Web3.HTTPProvider(
            self.provider.get()
        ))
        self.trans_spider = TransactionSpider(vm, net)
        self.trace_spider = TraceSpider(vm, net)
        self.rcpt_spider = ReceiptSpider(vm, net)
        self.abi_spider = ABISpider(vm, net)

    def parse_input(self, input: str, abi: ABI):
        if len(input[:10]) != 10:
            return None

        try:
            contract = self.w3.eth.contract(
                self.w3.to_checksum_address(abi.address),
                abi=abi.abi
            )
            func = contract.get_function_by_selector(input[:10])
            func_id = func.function_identifier
            func_entry = next((
                abi for abi in contract.abi if
                abi['type'] == 'function' and abi.get('name') == func_id
            ), None)
            if not func_entry:
                return None
            decoded_input = contract.decode_function_input(input)
            args = {
                param['name']: decoded_input[1].get(param['name'], None)
                for param in func_entry['inputs']
            }
            formal_params = ','.join([
                f"{param['type']} {param['name']}"
                for param in func_entry['inputs']
            ])
            return {
                'func': f"{func_id}({','.join(formal_params)})",
                'args': parse_hexbytes_dict(dict({
                    k: '0x' + v.hex().lstrip('0')
                    if isinstance(v, bytes) else v
                    for k, v in args.items()
                }))

            }
        except Exception as e:
            logging.error(e)
            return None

    async def parse(self, **kwargs):
        key = kwargs.get("id")
        hash = kwargs.get("hash")
        out = kwargs.get("out")

        tasks = [
            asyncio.create_task(self.trans_spider.crawl(params=[{'hash': hash, 'out': out}])),
            asyncio.create_task(self.trace_spider.crawl(params=[{'hash': hash, 'out': out}])),
            asyncio.create_task(self.rcpt_spider.crawl(params=[{'hash': hash, 'out': out}]))
        ]
        trans_queue, trace_queue, rcpt_queue = await asyncio.gather(*tasks)
        trans, trace, rcpt = trans_queue[0], trace_queue[0], rcpt_queue[0]

        if len(trans.item) == 0 or len(trace.item) == 0 or len(rcpt.item) == 0:
            return Result(key=key, item={})

        address = Receipt().map(rcpt.item).get_contract_address()
        if address != "None" and address is not None:
            address = get_impl_address(address, trace.item)
        abi_queue = await self.abi_spider.crawl(params=[{'address': address, 'out': out}])
        if len(abi_queue[0].item) == 0:
            return Result(key=key, item={})
        abi = abi_queue[0].item.dict().get('abi')

        res = self.parse_input(trans.item.dict().get('input'), ABI().map({
           'address': address,
           'abi': abi
        }))
        if res is None:
            return Result(key=key, item={})

        return Result(
            key=key, item=Input().map({
                'hash': hash,
                'func': res["func"],
                'args': res["args"]
            }).dict()
        )
#
# class CompleteFormParser(Parser):
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         super().__init__(vm, net, module)
#         self.tx_spider = TransactionSpider(vm, net, Module.TX)
#         self.el_parser = EventLogParser(vm, net, module)
#         self.in_parser = InputParser(vm, net, module)
#         self.sg_parser = SubgraphParser(vm, net, module)
#         self.ts_parser = TimestampParser(vm, net, module)
#
#     @save_item
#     @load_exists_item
#     @preprocess_keys
#     async def parse(self, keys: List[str], mode: Mode, out: str):
#         tasks = [
#             asyncio.create_task(self.tx_spider.crawl(keys, Mode.TRANS, out)),
#             asyncio.create_task(self.el_parser.parse(keys, Mode.EL, out)),
#             asyncio.create_task(self.in_parser.parse(keys, Mode.IN, out)),
#             asyncio.create_task(self.sg_parser.parse(keys, Mode.SG, out)),
#             asyncio.create_task(self.ts_parser.parse(keys, Mode.TS, out)),
#         ]
#         await asyncio.gather(*tasks)
#         trans_q, el_q, in_q, sg_q, ts_q = await asyncio.gather(*tasks)
#
#         common_idxs = set(range(len(keys)))
#         for q in [trans_q, el_q, in_q, sg_q, ts_q]:
#             common_idxs &= set(q.get_non_none_idx())
#
#         queue = ResultQueue()
#         for i, k in enumerate(keys):
#             if i not in common_idxs:
#                 queue.add(Result(key=k, item=None))
#             else:
#                 trans_ = trans_q[i].item.dict()
#                 ts_ = ts_q[i].item.dict()
#                 sg_ = sg_q[i].item.dict()
#                 in_ = in_q[i].item.dict()
#                 el_ = el_q[i].item.dict()
#
#                 queue.add(Result(
#                     key=k,
#                     item=CompleteForm().map({
#                         'tx': trans_,
#                         'timestamp': ts_.get("timestamp"),
#                         'subgraph': {'edges': sg_.get("edges"), 'nodes': sg_.get("nodes")},
#                         'input': {'func': in_.get('func'), 'args': in_.get('args')},
#                         'event_logs': el_.get('event_logs')
#                     })
#                 ))
#         return queue
#
#
# class EventLogParser(Parser):
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         super().__init__(vm, net, module)
#         self.w3 = Web3(Web3.HTTPProvider(
#             self.provider.get()
#         ))
#         self.tx_spider = TransactionSpider(vm, net, Module.TX)
#         self.sc_spider = ContractSpider(vm, net, Module.SC)
#
#     def get_event_signature(self, event: dict):
#         param_type, param_name = [], []
#         for param in event["inputs"]:
#             if "components" not in param:
#                 param_type.append(param["type"])
#                 param_name.append(param["name"])
#             else:
#                 param_type.append(f"({','.join([p['type'] for p in param['components']])})")
#                 param_name.append(f"({','.join([p['name'] for p in param['components']])})")
#
#         inputs = ",".join(param_type)
#         pt = ",".join([e.lstrip('(').rstrip(')') for e in param_type]).split(",")
#         pn = ",".join([e.lstrip('(').rstrip(')') for e in param_name]).split(",")
#         pv = [f"{a} {b}" for a, b in zip(pt, pn)]
#
#         # Hash event signature
#         event_signature_text = f"{event['name']}({inputs})"
#         event_signature = self.w3.to_hex(
#             self.w3.keccak(text=event_signature_text)
#         )
#         return pv, event_signature
#
#     def decoded_log(self, event, contract, receipt):
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")
#             try:
#                 decoded_log = dict(
#                     contract.events[event["name"]]().process_receipt(receipt)[0]
#                 )
#                 return decoded_log
#             except Exception as e:
#                 logging.error(e)
#         return None
#
#     def parse_event_logs(self, hash: str, abi_dict: dict):
#         event_logs = []
#         receipt = self.w3.eth.get_transaction_receipt(HexBytes(hash))
#         for idx, log in enumerate(receipt["logs"]):
#             addr = log["address"].lower()
#             if addr not in abi_dict:
#                 continue
#
#             contract = self.w3.eth.contract(
#                 self.w3.to_checksum_address(addr), abi=abi_dict[addr]
#             )
#             receipt_event_signature = self.w3.to_hex(log["topics"][0])
#
#             events = [e for e in contract.abi if e["type"] == "event"]
#             for event in events:
#                 pv, event_signature = self.get_event_signature(event)
#                 # Find match between log's event signature and ABI's event signature
#                 if event_signature != receipt_event_signature:
#                     continue
#
#                 decoded_log = self.decoded_log(event, contract, receipt)
#                 if decoded_log is None:
#                     continue
#                 event_logs.append(
#                     EventLog().map({
#                         'hash': hash,
#                         'address': addr,
#                         'event': f"{event['name']}({','.join(pv)})",
#                         'args': parse_hexbytes_dict(dict(decoded_log['args']))
#                     }).dict()
#                 )
#                 break
#         return event_logs
#
#     @save_item
#     @load_exists_item
#     @preprocess_keys
#     async def parse(self, keys: List[str], mode: Mode, out: str):
#         tasks = [
#             asyncio.create_task(self.tx_spider.crawl(keys, Mode.TRACE, out)),
#             asyncio.create_task(self.tx_spider.crawl(keys, Mode.RCPT, out))
#         ]
#         trace_queue, rcpt_queue = await asyncio.gather(*tasks)
#
#         common_idxs = set(range(len(keys)))
#         for q in [trace_queue, rcpt_queue]:
#             common_idxs &= set(q.get_non_none_idx())
#         addresses = [
#             get_impl_address(a, trace_queue[i].item.dict())
#             for i in common_idxs
#             for a in [rcpt_queue[i].item.get_contract_address()] +
#                      [e for e in rcpt_queue[i].item.get_event_sources()]
#             if a != "None" and a is not None
#         ]
#
#         abi_queue = await self.sc_spider.crawl(list(set(addresses)), Mode.ABI, out)
#         abi_dict = {e.key: e.item.dict().get('abi') for e in abi_queue if e.item is not None}
#
#         queue = ResultQueue()
#         for i, k in enumerate(keys):
#             if i not in common_idxs:
#                 queue.add(Result(key=k, item=None))
#                 continue
#             res = self.parse_event_logs(k, abi_dict)
#             if res is None:
#                 queue.add(Result(key=k, item=None))
#                 continue
#             queue.add(Result(key=k, item=EventLogs().map({'array': res})))
#         return queue
#
#

#
#
# class SubgraphParser(Parser):
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         super().__init__(vm, net, module)
#         self.spider = TransactionSpider(vm, net, Module.TX)
#
#     @save_item
#     @load_exists_item
#     @preprocess_keys
#     async def parse(self, keys: List[str], mode: str, out: str):
#         tasks = [
#             asyncio.create_task(self.spider.crawl(keys, Mode.TRANS, out)),
#             asyncio.create_task(self.spider.crawl(keys, Mode.TRACE, out))
#         ]
#         trans_queue, trace_queue = await asyncio.gather(*tasks)
#         common_idxs = set(range(len(keys)))
#         for q in [trans_queue, trace_queue]:
#             common_idxs &= set(q.get_non_none_idx())
#
#         queue = ResultQueue()
#         for i, k in enumerate(keys):
#             if i not in common_idxs:
#                 queue.add(Result(key=k, item=None))
#             else:
#                 paths = []
#                 trans = trans_queue[i].item.dict()
#                 paths.append({
#                     'from': trans.get('from_'),
#                     'to': trans.get('to_'),
#                 })
#                 trace = trace_queue[i].item.dict()
#                 paths = paths + [
#                     {
#                         'from': t.get('action').get('from_'),
#                         'to': t.get('action').get('to_'),
#                     }
#                     for t in trace['array']
#                 ]
#                 queue.add(Result(
#                     key=k,
#                     item=Subgraph().map({
#                         'hash': k,
#                         'paths': paths
#                     })
#                 ))
#         return queue



