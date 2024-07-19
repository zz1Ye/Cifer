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
from spider.meta import Spider, check_item_exists
from utils.conf import Net, Vm, Module
from utils.pc import Job, PC
from utils.req import Request, Headers


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.rpc = RPC_LIST.get(self.vm).get(self.module)

    async def get(self, **kwargs):
        mode = kwargs.get('mode')
        hash = kwargs.get('hash')

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

    @check_item_exists
    async def crawl(self, keys: List[str], mode: str, out: str):
        source = Queue()
        for hash in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'hash': hash},
                    item={
                        'trans': Transaction(),
                        'trace': Trace(), 'rcpt': Receipt()
                    }[mode],
                    dao=JsonDao(f"{out}/{hash}/{mode}.json")
                )
            )
        pc = PC(source)
        await pc.run()
        return list(pc.fi_q), list(pc.fa_q)


async def main():
    spider = TransactionSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.TX
    )
    res = await spider.get(mode='trace', hash='0x2f13d202c301c8c1787469310a2671c8b57837eb7a8a768df857cbc7b3ea32d8')
    print(res)

# asyncio.get_event_loop().run_until_complete(main())


