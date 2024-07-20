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
    except StopIteration:
        pass
    return address


class CompleteFormParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.tx_spider = TransactionSpider(vm, net, Module.TX)
        self.el_parser = EventLogParser(vm, net, module)
        self.in_parser = InputParser(vm, net, module)
        self.sg_parser = SubgraphParser(vm, net, module)
        self.ts_parser = TimestampParser(vm, net, module)

    @save_item
    @load_exists_item
    @preprocess_keys
    async def parse(self, keys: List[str], mode: Mode, out: str):
        tasks = [
            asyncio.create_task(self.tx_spider.crawl(keys, Mode.TRANS, out)),
            asyncio.create_task(self.el_parser.parse(keys, Mode.EL, out)),
            asyncio.create_task(self.in_parser.parse(keys, Mode.IN, out)),
            asyncio.create_task(self.sg_parser.parse(keys, Mode.SG, out)),
            asyncio.create_task(self.ts_parser.parse(keys, Mode.TS, out)),
        ]
        trans_q, el_q, in_q, sg_q, ts_q = await asyncio.gather(*tasks)

        common_idxs = set(range(len(keys)))
        for q in [trans_q, el_q, in_q, sg_q, ts_q]:
            common_idxs &= set([i for i, e in enumerate(q) if e['item'] is not None])

        queue = []
        for i, k in enumerate(keys):
            if i not in common_idxs:
                queue.append({'key': k, 'item': None})
            else:
                trans_ = trans_q[i].get('item')
                ts_ = ts_q[i].get('item')
                sg_ = sg_q[i].get('item')
                in_ = in_q[i].get('item')
                el_ = el_q[i].get('item')

                queue.append({'key': keys[i], 'item': {
                    'tx': trans_,
                    'timestamp': ts_.get("timestamp"),
                    'subgraph': {'edges': sg_.get("edges"), 'nodes': sg_.get("nodes")},
                    'input': {'func': in_.get('func'), 'args': in_.get('args')},
                    'event_logs': el_.get('event_logs')
                }})
        return queue


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

        common_idxs = set(range(len(keys)))
        for q in [trace_queue, rcpt_queue]:
            common_idxs &= set([i for i, e in enumerate(q) if e['item'] is not None])

        addresses = {}
        for i in common_idxs:
            item = rcpt_queue[i].get('item')
            address = item.get('contract_address', None)
            address = item.get('to_') if address is None else address
            addresses[address] = get_impl_address(address, trace_queue[i].get('item'))

            for log in item.get('logs', []):
                address = log.get("address", None)
                if address is not None:
                    addresses[address] = get_impl_address(address, trace_queue[i].get('item'))

        abi_queue = await self.sc_spider.crawl([v for _, v in addresses.items()], Mode.ABI, out)
        abi_dict = {e['key']: e.get('item').get('abi') for e in abi_queue if e.get('item') is not None}

        queue = []
        for i, k in enumerate(keys):
            if i not in common_idxs:
                queue.append({'key': k, 'item': None})
            else:
                receipt = self.w3.eth.get_transaction_receipt(HexBytes(k))
                event_logs = []
                for idx, log in enumerate(receipt["logs"]):
                    addr = log["address"].lower()
                    if addr not in abi_dict:
                        continue

                    contract = self.w3.eth.contract(
                        self.w3.to_checksum_address(addr), abi=abi_dict[addr]
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
                                        'address': addr,
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

        common_idxs = set(range(len(keys)))
        for q in [trans_queue, trace_queue, rcpt_queue]:
            common_idxs &= set([i for i, e in enumerate(q) if e['item'] is not None])

        addresses = {}
        for i in common_idxs:
            item = rcpt_queue[i].get('item')
            address = item.get('contract_address', None)
            address = item.get('to_') if address is None else address
            addresses[i] = address

        abi_queue = await self.sc_spider.crawl([v for _, v in addresses.items()], Mode.ABI, out)
        abi_dict = {e['key']: e.get('item').get('abi') for e in abi_queue if e.get('item') is not None}

        queue = []
        for i, k in enumerate(keys):
            if i not in common_idxs:
                queue.append({'key': k, 'item': None})
            else:
                address = addresses[i]
                if address not in abi_dict:
                    queue.append({'key': k, 'item': None})
                else:
                    item = trans_queue[i].get('item')
                    function_signature = item['input'][:10]
                    input = {'func': '', 'args': {}}
                    if len(function_signature) == 10:
                        contract = self.w3.eth.contract(
                            self.w3.to_checksum_address(address),
                            abi=abi_dict[address]
                        )
                        function = contract.get_function_by_selector(function_signature)

                        function_abi_entry = next(
                            (
                                abi for abi in contract.abi if
                                abi['type'] == 'function' and abi.get('name') == function.function_identifier
                            ), None)

                        if function_abi_entry:
                            decoded_input = contract.decode_function_input(item['input'])

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
        common_idxs = set(range(len(keys)))
        for q in [trans_queue, trace_queue]:
            common_idxs &= set([i for i, e in enumerate(q) if e['item'] is not None])

        queue = []
        for i, k in enumerate(keys):
            if i not in common_idxs:
                queue.append({'key': k, 'item': None})
            else:
                paths = []
                trans = trans_queue[i]
                paths.append({
                    'from': trans.get('item').get('from_'),
                    'to': trans.get('item').get('to_'),
                })
                trace = trace_queue[i]
                paths = paths + [
                    {
                        'from': t.get('action').get('from_'),
                        'to': t.get('action').get('to_'),
                    }
                    for t in trace.get('item')['array']
                ]
                queue.append({'key': k, 'item': Subgraph().map({
                    'hash': k,
                    'paths': paths
                }).dict()})
        return queue


class TimestampParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.blk_spider = BlockSpider(vm, net, Module.BLK)
        self.tx_spider = TransactionSpider(vm, net, Module.TX)

    @save_item
    @load_exists_item
    @preprocess_keys
    async def parse(self, keys: List[str], mode: Mode, out: str):
        trans_queue = await self.tx_spider.crawl(keys, Mode.TRANS, out)

        trans_dict = {}
        blk_hash_arr = set()
        for e in trans_queue:
            item = e.get("item")
            trans_dict[e.get('key')] = item
            if item is not None:
                blk_hash_arr.add(item.get("block_hash"))

        block_queue = await self.blk_spider.crawl(list(blk_hash_arr), Mode.BLOCK, out)
        block_dict = {}
        for e in block_queue:
            item = e.get("item")
            if item is not None:
                block_dict[item.get('hash')] = item.get('timestamp')

        queue = []
        for k in keys:
            if trans_dict.get(k) is None:
                queue.append({'key': k, 'item': None})
            else:
                trans = trans_dict.get(k)
                queue.append({'key': k, 'item': Timestamp().map({
                    'hash': k,
                    'timestamp': block_dict.get(trans.get('block_hash')),
                    'block_number': trans.get('block_number')
                }).dict()})
        return queue


