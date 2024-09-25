import asyncio
import logging
import warnings
from typing import List

from hexbytes import HexBytes

from item.evm.ac import ABI
from item.evm.ps import Input, EventLogs, EventLog, Timestamp, FundsFlowSubgraph
from item.evm.tx import Receipt
from spider._meta import Parser, Param
from spider.dec import CacheSpider
from spider.evm_.ac import ABISpider, TxListSpider
from spider.evm_.blk import BlockSpider
from spider.evm_.tx import TransactionSpider, TraceSpider, ReceiptSpider
from utils.conf import Vm, Net, Module, Mode
from utils.req import Result
from utils.web3 import parse_hexbytes_dict


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


class InputParser(Parser):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.PS, Mode.IN

        self.trans_spider = CacheSpider(TransactionSpider(vm, net))
        self.trace_spider = CacheSpider(TraceSpider(vm, net))
        self.rcpt_spider = CacheSpider(ReceiptSpider(vm, net))
        self.abi_spider = CacheSpider(ABISpider(vm, net))

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
                'func': f"{func_id}({formal_params})",
                'args': parse_hexbytes_dict(dict({
                    k: '0x' + v.hex().lstrip('0')
                    if isinstance(v, bytes) else v
                    for k, v in args.items()
                }))

            }
        except Exception as e:
            logging.error(e)
            return None

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.id, p.query.get("hash")
            tasks = [
                asyncio.create_task(self.trans_spider.parse([Param(query={'hash': hash})])),
                asyncio.create_task(self.trace_spider.parse([Param(query={'hash': hash})])),
                asyncio.create_task(self.rcpt_spider.parse([Param(query={'hash': hash})]))
            ]
            trans, trace, rcpt = await asyncio.gather(*tasks)
            trans, trace, rcpt = trans[0], trace[0], rcpt[0]

            if len(trans.item) == 0 or len(trace.item) == 0 or len(rcpt.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            address = Receipt().map(rcpt.item).get_contract_address()
            if address != "None" and address is not None:
                address = get_impl_address(address, trace.item)
            abi = await self.abi_spider.parse([Param(query={'address': address})])
            abi = abi[0]
            if len(abi.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            res = self.parse_input(trans.item.get('input'), ABI().map({
               'address': address,
               'abi': abi.item.get('abi')
            }))
            if res is None:
                res_arr.append(Result(key=key, item={}))
                continue

            res_arr.append(
                Result(
                    key=key, item=Input().map({
                        'hash': hash,
                        'func': res["func"],
                        'args': res["args"]
                    }).dict()
                )
            )
        return res_arr


class EventLogParser(Parser):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.PS, Mode.EL

        self.trace_spider = CacheSpider(TraceSpider(vm, net))
        self.rcpt_spider = CacheSpider(ReceiptSpider(vm, net))
        self.abi_spider = CacheSpider(ABISpider(vm, net))

    def get_event_signature(self, event: dict):
        param_type, param_name = [], []
        for param in event["inputs"]:
            if "components" not in param:
                param_type.append(param["type"])
                param_name.append(param["name"])
            else:
                param_type.append(f"({','.join([p['type'] for p in param['components']])})")
                param_name.append(f"({','.join([p['name'] for p in param['components']])})")

        inputs = ",".join(param_type)
        pt = ",".join([e.lstrip('(').rstrip(')') for e in param_type]).split(",")
        pn = ",".join([e.lstrip('(').rstrip(')') for e in param_name]).split(",")
        pv = [f"{a} {b}" for a, b in zip(pt, pn)]

        # Hash event signature
        event_signature_text = f"{event['name']}({inputs})"
        event_signature = self.w3.to_hex(
            self.w3.keccak(text=event_signature_text)
        )
        return pv, event_signature

    def decoded_log(self, event, contract, receipt):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                decoded_log = dict(
                    contract.events[event["name"]]().process_receipt(receipt)[0]
                )
                return decoded_log
            except Exception as e:
                logging.error(e)
        return None

    def parse_event_logs(self, hash: str, abi_dict: dict):
        event_logs = []
        receipt = self.w3.eth.get_transaction_receipt(HexBytes(hash))
        for idx, log in enumerate(receipt["logs"]):
            addr = log["address"].lower()
            if addr not in abi_dict:
                continue

            contract = self.w3.eth.contract(
                self.w3.to_checksum_address(addr), abi=abi_dict[addr]
            )
            receipt_event_signature = self.w3.to_hex(log["topics"][0])

            events = [e for e in contract.abi if e["type"] == "event"]
            for event in events:
                pv, event_signature = self.get_event_signature(event)
                # Find match between log's event signature and ABI's event signature
                if event_signature != receipt_event_signature:
                    continue

                decoded_log = self.decoded_log(event, contract, receipt)
                if decoded_log is None:
                    continue
                event_logs.append(
                    EventLog().map({
                        'hash': hash,
                        'address': addr,
                        'event': f"{event['name']}({','.join(pv)})",
                        'args': parse_hexbytes_dict(dict(decoded_log['args']))
                    }).dict()
                )
                break
        return event_logs

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.id, p.query.get("hash")
            tasks = [
                asyncio.create_task(self.trace_spider.parse([Param(query={'hash': hash})])),
                asyncio.create_task(self.rcpt_spider.parse([Param(query={'hash': hash})]))
            ]
            trace, rcpt = await asyncio.gather(*tasks)
            trace, rcpt = trace[0], rcpt[0]
            if len(trace.item) == 0 or len(rcpt.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            addresses = [Receipt().map(rcpt.item).get_contract_address()]
            addresses += Receipt().map(rcpt.item).get_event_sources()
            impl_address = [
                get_impl_address(addr, trace.item)
                if addr != "None" and addr is not None
                else addr
                for addr in addresses
            ]

            abi_dict = {}
            abi_arr = await self.abi_spider.parse([
                Param(query={'address': addr}) for addr in impl_address
            ])
            for i, addr in enumerate(addresses):
                abi = abi_arr[i]
                if len(abi.item) != 0:
                    abi_dict[addr.lower()] = abi.item.get('abi')

            res = self.parse_event_logs(hash, abi_dict)
            if res is None or len(res) == 0 :
                res_arr.append(Result(key=key, item={}))
                continue

            res_arr.append(Result(key=key, item=EventLogs().map({'array': res}).dict()))
        return res_arr


class TimestampParser(Parser):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.PS, Mode.TS

        self.trans_spider = CacheSpider(TransactionSpider(vm, net))
        self.block_spider = CacheSpider(BlockSpider(vm, net))

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.id, p.query.get("hash")
            trans = await self.trans_spider.parse([Param(query={'hash': hash})])
            trans = trans[0]
            if len(trans.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            block = await self.block_spider.parse([Param(query={'hash': trans.item.get("block_hash")})])
            block = block[0]
            if len(block.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            res_arr.append(
                Result(
                    key=key, item=Timestamp().map({
                        'hash': hash,
                        'timestamp': block.item.get('timestamp'),
                        'block_number': trans.item.get('block_number')
                    }).dict()
                )
            )
        return res_arr


class FundsFlowSubgraphSpider(Parser):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.PS, Mode.FFS
        self.trans_spider = CacheSpider(TransactionSpider(vm, net))
        self.txlist_spider = CacheSpider(TxListSpider(vm, net))

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.id, p.query.get("hash")
            trans = await self.trans_spider.parse([Param(query={'hash': hash})])
            trans = trans[0]
            if len(trans.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            block_number = trans.item.get("block_number")
            tx_list = await self.txlist_spider.parse([
                Param(query={
                    'address': trans.item.get("from_"),
                    'start_blk': block_number, 'end_blk': block_number,
                }),
                Param(query={
                    'address': trans.item.get("to_"),
                    'start_blk': block_number, 'end_blk': block_number,
                }),
            ])
            print(tx_list)
            exit(0)
            from_res, to_res = tx_list[0], tx_list[1]
            if len(from_res.item) == 0 and len(to_res.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

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

            res_arr.append(
                Result(
                    key=key, item=FundsFlowSubgraph().map({
                        'hash': hash,
                        'edges': edges,
                        'nodes': list(set(nodes))
                    }) if len(nodes) != 0 else {}
                )
            )

        return res_arr
