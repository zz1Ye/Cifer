#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ps.py
@Time   : 2024/7/18 12:15
@Author : zzYe

"""
from queue import Queue
from typing import List

from dao.meta import JsonDao
from item.evm.blk import Block
from item.evm.ps import Timestamp
from item.evm.tx import Transaction, Trace
from spider.evm.blk import BlockSpider
from spider.evm.tx import TransactionSpider
from spider.meta import Parser
from utils.conf import Vm, Net, Module
from utils.pc import Job, PC


class SubgraphParser(Parser):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.spider = TransactionSpider(vm, net, module)

    async def parse(self, hashes: List[str], out: str):
        source = Queue()
        for h in hashes:
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

    async def parse(self, hashes: List[str], out: str):
        source = Queue()
        mode = "block"
        for h in hashes:
            dao = JsonDao(f"{out}/{h}/{mode}.json")
            source.put(
                Job(
                    spider=self.spider,
                    params={'mode': mode, 'hash': h},
                    item=Block(),
                    dao=dao
                )
            )

        pc = PC(source)
        await pc.run()

        ts_d = {}
        while pc.fi_q.qsize() != 0:
            item = pc.fi_q.get()
            hash = item['hash']

            ts_d[hash] = Timestamp().map(item)
        return ts_l


