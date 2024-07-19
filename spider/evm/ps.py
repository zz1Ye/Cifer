#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ps.py
@Time   : 2024/7/18 12:15
@Author : zzYe

"""
import warnings
from queue import Queue
from typing import List

from hexbytes import HexBytes
from web3 import Web3

from dao.meta import JsonDao
from item.evm.blk import Block
from item.evm.ps import Timestamp
from item.evm.sc import ABI
from item.evm.tx import Transaction, Trace, Receipt
from spider.evm.blk import BlockSpider
from spider.evm.sc import ContractSpider
from spider.evm.tx import TransactionSpider
from spider.meta import Parser, check_item_exists, preprocess_keys
from utils.conf import Vm, Net, Module
from utils.pc import Job, PC
from utils.web3 import parse_hexbytes_dict


class EventLogParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.w3 = Web3(Web3.HTTPProvider(
            self.provider.get()
        ))
        self.trans_spider = TransactionSpider(vm, net, module)
        self.abi_spider = ContractSpider(vm, net, Module.SC)

    @check_item_exists
    @preprocess_keys
    async def parse(self, keys: List[str], mode: str, out: str):
        source = Queue()
        for h in keys:
            for mode in ['trace', 'rcpt']:
                source.put(
                    Job(
                        spider=self.trans_spider,
                        params={'mode': mode, 'hash': h},
                        item={'trans': Transaction(), 'trace': Trace(), 'rcpt': Receipt()}[mode],
                        dao=JsonDao(f"{out}/tx/{h}/{mode}.json")
                    )
                )

        pc = PC(source)
        await pc.run()

        tx_d = {}
        while pc.fi_q.qsize() != 0:
            item = pc.fi_q.get().item
            if isinstance(item, Receipt):
                item = item.dict()
                hash = item['transaction_hash']
                rcpt = Receipt()
                rcpt.map(item)
                if hash not in tx_d:
                    tx_d[hash] = {}
                tx_d[hash]['address'] = rcpt.to_ if rcpt.contract_address is None else rcpt.contract_address
            else:
                item = item.dict()
                traces = []
                for t in item['array']:
                    hash = t['transaction_hash']
                    traces.append(t['action'])

                if hash not in tx_d:
                    tx_d[hash] = {}
                tx_d[hash]['traces'] = traces

        source = Queue()
        for k, v in tx_d.items():
            print(v['address'])
            try:
                addr = next(
                    t["to_"]
                    for t in v['traces']
                    if (
                            t["call_type"].lower() == "delegatecall"
                            and t["from_"] == v['address']
                    )
                )
            except StopIteration:
                addr = v['address']
            source.put(
                Job(
                    spider=self.abi_spider,
                    params={'mode': 'abi', 'address': addr},
                    item=ABI(),
                    dao=JsonDao(f"{out}/sc/{addr}/abi.json")
                )
            )

        pc = PC(source)
        await pc.run()

        ad_d = {}
        while pc.fi_q.qsize() != 0:
            item = pc.fi_q.get().item
            item = item.dict()
            address = item['address']
            abi = ABI()
            abi.map(item)
            if address not in ad_d:
                ad_d[address] = {}
            ad_d[address]['abi'] = abi.abi

        el_d = {}
        for k, v in tx_d.items():
            receipt = self.w3.eth.get_transaction_receipt(HexBytes(hash))
            event_logs = []
            for idx, log in enumerate(receipt["logs"]):
                addr = log["address"].lower()
                contract = self.w3.eth.contract(
                    self.w3.to_checksum_address(addr), abi=ad_d[v['address']]['abi']
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
                                {
                                    'event': f"{name}({','.join(p_p)})",
                                    'args': parse_hexbytes_dict(dict(decoded_log['args']))
                                }
                            )
                            break
            el_d[k] = event_logs
        return el_d


class InputParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.w3 = Web3(Web3.HTTPProvider(
            self.provider.get()
        ))
        self.trans_spider = TransactionSpider(vm, net, module)
        self.abi_spider = ContractSpider(vm, net, Module.SC)

    @check_item_exists
    @preprocess_keys
    async def parse(self, keys: List[str], mode: str, out: str):
        source = Queue()
        for h in keys:
            for mode in ['trans', 'trace', 'rcpt']:
                source.put(
                    Job(
                        spider=self.trans_spider,
                        params={'mode': mode, 'hash': h},
                        item={'trans': Transaction(), 'trace': Trace(), 'rcpt': Receipt()}[mode],
                        dao=JsonDao(f"{out}/tx/{h}/{mode}.json")
                    )
                )

        pc = PC(source)
        await pc.run()

        tx_d = {}
        while pc.fi_q.qsize() != 0:
            item = pc.fi_q.get().item

            if isinstance(item, Transaction):
                item = item.dict()
                hash = item['hash']
                trans = Transaction()
                trans.map(item)
                if hash not in tx_d:
                    tx_d[hash] = {}
                tx_d[hash]['input'] = trans.input
            elif isinstance(item, Receipt):
                item = item.dict()
                hash = item['transaction_hash']
                rcpt = Receipt()
                rcpt.map(item)
                if hash not in tx_d:
                    tx_d[hash] = {}
                tx_d[hash]['address'] = rcpt.to_ if rcpt.contract_address is None else rcpt.contract_address
            else:
                item = item.dict()
                traces = []
                for t in item['array']:
                    hash = t['transaction_hash']
                    traces.append(t['action'])

                if hash not in tx_d:
                    tx_d[hash] = {}
                tx_d[hash]['traces'] = traces

        source = Queue()
        for k, v in tx_d.items():
            print(v['address'])
            try:
                addr = next(
                    t["to_"]
                    for t in v['traces']
                    if (
                            t["call_type"].lower() == "delegatecall"
                            and t["from_"] == v['address']
                    )
                )
            except StopIteration:
                addr = v['address']
            source.put(
                Job(
                    spider=self.abi_spider,
                    params={'mode': 'abi', 'address': addr},
                    item=ABI(),
                    dao=JsonDao(f"{out}/sc/{addr}/abi.json")
                )
            )

        pc = PC(source)
        await pc.run()

        ad_d = {}
        while pc.fi_q.qsize() != 0:
            item = pc.fi_q.get().item
            item = item.dict()
            address = item['address']
            abi = ABI()
            abi.map(item)
            if address not in ad_d:
                ad_d[address] = {}
            ad_d[address]['abi'] = abi.abi

        in_d = {}
        for k, v in tx_d.items():
            function_signature = v['input'][:10]
            input = {'func': '', 'args': {}}
            if len(function_signature) == 10:
                contract = self.w3.eth.contract(
                    self.w3.to_checksum_address(v['address']),
                    abi=ad_d[v['address']]['abi']
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
            in_d[k] = input
        return in_d


class SubgraphParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.spider = TransactionSpider(vm, net, module)

    @check_item_exists
    @preprocess_keys
    async def parse(self, keys: List[str], mode: str, out: str):
        trans_fi, trans_fa = await self.spider.crawl(keys, 'trans', out)
        trans_fi = [{
            'hash': job.item.hash,
            'from': job.item.from_,
            'to': job.item.to_
        } for job in trans_fi]

        trans_fa = [
            job.id.split("-")[1]
            for job in trans_fa
        ]

        source = Queue()
        for h in keys:
            for mode in ['trans', 'trace']:
                source.put(
                    Job(
                        spider=self.spider,
                        params={'mode': mode, 'hash': h},
                        item={'trans': Transaction(), 'trace': Trace()}[mode],
                        dao=JsonDao(f"{out}/{h}/{mode}.json")
                    )
                )

        pc = PC(source)
        await pc.run()

        sg_d = {}
        while pc.fi_q.qsize() != 0:
            item = pc.fi_q.get().item
            print(item)

            if isinstance(item, Transaction):
                item = item.dict()
                hash = item['hash']
                if hash not in sg_d:
                    sg_d[hash] = []
                sg_d[hash].append({'from': item['from_address'], 'to': item['to_address']})
            else:
                item = item.dict()
                for e in item['array']:
                    hash = e['transaction_hash']
                    action = e['action']
                    if hash not in sg_d:
                        sg_d[hash] = []
                    sg_d[hash].append({'from': action['from_address'], 'to': action['to_address']})

        return sg_d


class TimestampParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.spider = BlockSpider(vm, net, module)

    @check_item_exists
    @preprocess_keys
    async def parse(self, keys: List[str], mode: str, out: str):
        fi, fa = await self.spider.crawl(keys, 'block', out)

        n_fi = [
            Timestamp().map({
                'hash': job.item.hash,
                'timestamp': job.item.timestamp,
                'blockNumber': job.item.block_number
            })
            for job in fi
        ]

        n_fa = [
            job.id.split("-")[1]
            for job in fa
        ]
        return n_fi, n_fa


