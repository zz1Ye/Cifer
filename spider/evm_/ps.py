import asyncio
import logging
import warnings
from typing import List, Dict

from hexbytes import HexBytes
from web3 import Web3

from item.evm.ac import ABI
from item.evm.ps import FundsFlowSubgraph, Timestamp, Input
from item.evm.tx import Receipt
from settings import HEADER
from spider._meta import Parser
from spider.evm.ac import TxListSpider, ABISpider
from spider.evm.blk import BlockSpider
from spider.evm.tx import TransactionSpider, TraceSpider, ReceiptSpider
from utils.conf import Vm, Net, Module, Mode
from utils.req import Request, Headers, Result
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

    async def parse(self, params: List[Dict]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.get("id"), p.get("hash")
            tasks = [
                asyncio.create_task(self.trans_spider.parse(id=hash, hash=hash)),
                asyncio.create_task(self.trace_spider.parse(id=hash, hash=hash)),
                asyncio.create_task(self.rcpt_spider.parse(id=hash, hash=hash))
            ]
            trans, trace, rcpt = await asyncio.gather(*tasks)

            if len(trans.item) == 0 or len(trace.item) == 0 or len(rcpt.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            address = Receipt().map(rcpt.item).get_contract_address()
            if address != "None" and address is not None:
                address = get_impl_address(address, trace.item)
            abi = await self.abi_spider.parse(id=address, address=address)
            if len(abi.item) == 0:
                res_arr.append(Result(key=key, item={}))
                continue

            res = self.parse_input(trans.item.dict().get('input'), ABI().map({
               'address': address,
               'abi': abi.item.dict().get('abi')
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

