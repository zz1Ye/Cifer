#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ts.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
import asyncio
from queue import Queue
from typing import List

from dao.meta import JsonDao
from item.evm.tx import Transaction, Trace, Receipt
from settings import RPC_LIST, HEADER
from spider.meta import Spider, check_item_exists, preprocess_keys, save_item
from utils.conf import Net, Vm, Module
from utils.pc import Job, PC, Status
from utils.req import Request, Headers


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.rpc = RPC_LIST.get(self.vm).get(self.module)

    async def get(self, **kwargs):
        mode = kwargs.get('mode')
        hash = kwargs.get('key')

        if mode not in ["trans", "trace", "rcpt"]:
            raise ValueError()

        payload = self.rpc.get(mode).get("payload")
        payload["params"] = [hash]
        req = Request(
            url=self.provider.get(),
            method=self.rpc.get(mode).get("method"),
            headers=Headers(
                accept=HEADER.get("accept"),
                content_type=HEADER.get("content-type"),
                user_agents=HEADER.get("user-agents"),
            ).get(),
            payload=payload
        )
        res = await self.fetch(req)
        if mode == 'trace':
            return {'res': res if res is None else {'array': res}, 'task': f'tx.{mode}'}
        return {'res': res, 'task': f'tx.{mode}'}

    @save_item
    @check_item_exists
    @preprocess_keys
    async def crawl(self, keys: List[str], mode: str, out: str):
        source = Queue()
        for hash in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'key': hash},
                    item={
                        'trans': Transaction(),
                        'trace': Trace(), 'rcpt': Receipt()
                    }[mode],
                    dao=JsonDao(f"{out}/{hash}/{mode}.json")
                )
            )
        pc = PC(source)
        await pc.run()
        queue = []
        while pc.fi_q.qsize() != 0:
            job = pc.fi_q.get()
            print(job.id.split('-'))
            queue.append({'key': job.id.split('-')[1], 'item': job.item.dict()})
        while pc.fa_q.qsize() != 0:
            job = pc.fa_q.get()
            queue.append({'key': job.id.split('-')[1], 'item': None})

        return queue


async def main():
    spider = TransactionSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.TX
    )
    res = await spider.get(mode='trace', hash='0x2f13d202c301c8c1787469310a2671c8b57837eb7a8a768df857cbc7b3ea32d8')
    print(res)

# asyncio.get_event_loop().run_until_complete(main())


