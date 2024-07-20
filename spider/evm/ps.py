#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ps.py
@Time   : 2024/7/18 12:15
@Author : zzYe

"""
import asyncio
import warnings
from collections import defaultdict
from typing import List

from hexbytes import HexBytes
from web3 import Web3

from item.evm.ps import Timestamp, Subgraph, Input, EventLog
from spider.evm.blk import BlockSpider
from spider.evm.sc import ContractSpider
from spider.evm.tx import TransactionSpider
from spider.meta import Parser, preprocess_keys, save_item, load_exists_item
from utils.conf import Vm, Net, Module, Mode
from utils.web3 import parse_hexbytes_dict


def get_impl_address(trace: dict, rcpt: dict):
    trace_arr = trace.get('array', [])
    contract_address = rcpt.get('contract_address', None)
    address = rcpt.get('to_') if contract_address is None else contract_address
    try:
        address = next(
            t.get('action', {}).get('to_')
            for t in trace_arr
            if (
                    t.get('action', {}).get('call_type').lower() == "delegatecall"
                    and t.get('action', {}).get('from_') == address
            )
        )
    except StopIteration:
        pass
    return address


class EventLogParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.w3 = Web3(Web3.HTTPProvider(
            self.provider.get()
        ))
        self.tx_spider = TransactionSpider(vm, net, Module.TX)
        self.sc_spider = ContractSpider(vm, net, Module.SC)

    @save_item
    @load_exists_item
    @preprocess_keys
    async def parse(self, keys: List[str], mode: Mode, out: str):
        tasks = [
            asyncio.create_task(self.tx_spider.crawl(keys, Mode.TRACE, out)),
            asyncio.create_task(self.tx_spider.crawl(keys, Mode.RCPT, out))
        ]
        trace_queue, rcpt_queue = await asyncio.gather(*tasks)
        trace_dict = {e.get('key'): e.get('item') for e in trace_queue}
        rcpt_dict = {e.get('key'): e.get('item') for e in rcpt_queue}

        tmp = {}
        for h in set(trace_dict.keys()) & set(rcpt_dict.keys()):
            print(trace_dict[h])
            address = get_impl_address(trace_dict[h], rcpt_dict[h])
            tmp[h] = {'address': address}

        abi_queue = await self.sc_spider.crawl([v.get('address') for v in tmp.values()], Mode.ABI, out)
        abi_dict = {e['key']: e.get('item').get('abi') for e in abi_queue if e.get('item') is not None}

        queue = []
        for k, v in tmp.items():
            if v.get('address') in abi_dict:
                receipt = self.w3.eth.get_transaction_receipt(HexBytes(k))
                event_logs = []
                for idx, log in enumerate(receipt["logs"]):
                    addr = log["address"].lower()
                    contract = self.w3.eth.contract(
                        self.w3.to_checksum_address(addr), abi=abi_dict[v['address']]
                    )
                    receipt_event_signature_hex = self.w3.to_hex(
                        log["topics"][0]
                    )

                    events = [e for e in contract.abi if e["type"] == "event"]
                    for event in events:
                        # Get event signature components
                        name = event["name"]
                        param_type, param_name = [], []

                        for param in event["inputs"]:
                            if "components" not in param:
                                param_type.append(param["type"])
                                param_name.append(param["name"])
                            else:
                                param_type.append(f"({','.join([p['type'] for p in param['components']])})")
                                param_name.append(f"({','.join([p['name'] for p in param['components']])})")

                        inputs = ",".join(param_type)
                        p_t = ",".join([e.lstrip('(').rstrip(')') for e in param_type]).split(",")
                        p_n = ",".join([e.lstrip('(').rstrip(')') for e in param_name]).split(",")
                        p_p = [f"{a} {b}" for a, b in zip(p_t, p_n)]

                        # Hash event signature
                        event_signature_text = f"{name}({inputs})"
                        event_signature_hex = self.w3.to_hex(
                            self.w3.keccak(text=event_signature_text)
                        )

                        # Find match between log's event signature and ABI's event signature
                        if event_signature_hex == receipt_event_signature_hex:
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore")
                                decoded_log = dict(contract.events[event["name"]]().process_receipt(receipt)[0])
                                event_logs.append(
                                    EventLog().map({
                                        'hash': k,
                                        'event': f"{name}({','.join(p_p)})",
                                        'args': parse_hexbytes_dict(dict(decoded_log['args']))
                                    }).dict()
                                )
                                break
                queue.append({
                    'key': k,
                    'item': {'event_logs': event_logs}
                })
        return queue


class InputParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.w3 = Web3(Web3.HTTPProvider(
            self.provider.get()
        ))
        self.tx_spider = TransactionSpider(vm, net, Module.TX)
        self.sc_spider = ContractSpider(vm, net, Module.SC)

    @save_item
    @load_exists_item
    @preprocess_keys
    async def parse(self, keys: List[str], mode: str, out: str):
        tasks = [
            asyncio.create_task(self.tx_spider.crawl(keys, Mode.TRANS, out)),
            asyncio.create_task(self.tx_spider.crawl(keys, Mode.TRACE, out)),
            asyncio.create_task(self.tx_spider.crawl(keys, Mode.RCPT, out))
        ]
        trans_queue, trace_queue, rcpt_queue = await asyncio.gather(*tasks)
        trans_dict = {e.get('key'): e.get('item') for e in trans_queue}
        trace_dict = {e.get('key'): e.get('item') for e in trace_queue}
        rcpt_dict = {e.get('key'): e.get('item') for e in rcpt_queue}

        tmp = {}
        for h in set(trans_dict.keys()) & set(trace_dict.keys()) & set(rcpt_dict.keys()):
            address = get_impl_address(trace_dict[h], rcpt_dict[h])
            tmp[h] = {'address': address, 'input': trans_dict[h]['input']}

        abi_queue = await self.sc_spider.crawl([v.get('address') for v in tmp.values()], Mode.ABI, out)
        abi_dict = {e['key']: e.get('item').get('abi') for e in abi_queue if e.get('item') is not None}

        queue = []
        for k, v in tmp.items():
            if v.get('address') in abi_dict:
                function_signature = v['input'][:10]
                input = {'func': '', 'args': {}}
                if len(function_signature) == 10:
                    contract = self.w3.eth.contract(
                        self.w3.to_checksum_address(v['address']),
                        abi=abi_dict[v['address']]
                    )
                    function = contract.get_function_by_selector(function_signature)

                    function_abi_entry = next(
                        (
                            abi for abi in contract.abi if
                            abi['type'] == 'function' and abi.get('name') == function.function_identifier
                        ), None)

                    if function_abi_entry:
                        decoded_input = contract.decode_function_input(v['input'])

                        args, formal_params = {}, []
                        for param in function_abi_entry['inputs']:
                            param_name, param_type = param['name'], param['type']
                            param_value = decoded_input[1].get(param_name, None)

                            formal_params.append(f"{param_type} {param_name}")
                            if isinstance(param_value, bytes):
                                args[param_name] = '0x' + param_value.hex().lstrip('0')
                            else:
                                args[param_name] = param_value

                        input["func"] = f"{function.function_identifier}({','.join(formal_params)})"
                        input["args"] = parse_hexbytes_dict(dict(args))
                queue.append({
                    'key': k,
                    'item': Input().map({
                        'hash': k,
                        'func': input["func"],
                        'args': input["args"]
                    }).dict()
                })
        return queue


class SubgraphParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.spider = TransactionSpider(vm, net, Module.TX)

    @save_item
    @load_exists_item
    @preprocess_keys
    async def parse(self, keys: List[str], mode: str, out: str):
        tasks = [
            asyncio.create_task(self.spider.crawl(keys, Mode.TRANS, out)),
            asyncio.create_task(self.spider.crawl(keys, Mode.TRACE, out))
        ]
        trans_queue, trace_queue = await asyncio.gather(*tasks)

        res = defaultdict(list)
        for e in trans_queue:
            res[e.get('key')].append({
                'from': e.get('item').get('from_'),
                'to': e.get('item').get('to_'),
            })

        for e in trace_queue:
            item = e.get('item')
            res[e.get('key')] += [
                {
                    'from': t.get('action').get('from_'),
                    'to': t.get('action').get('to_'),
                }
                for t in item['array']
            ]

        queue = []
        for k, v in res.items():
            queue.append({'key': k, 'item': Subgraph().map({
                'hash': k,
                'paths': v
            }).dict()})

        return queue


class TimestampParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.spider = BlockSpider(vm, net, Module.BLK)

    @save_item
    @load_exists_item
    @preprocess_keys
    async def parse(self, keys: List[str], mode: str, out: str):
        queue = await self.spider.crawl(keys, Mode.BLOCK, out)

        for i in range(len(queue)):
            item = queue[i].get("item")
            if item is not None:
                queue[i]['item'] = Timestamp().map({
                    'hash': item['hash'],
                    'timestamp': item['timestamp'],
                    'blockNumber': item['block_number']
                }).dict()
        return queue


