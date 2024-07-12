#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : tx.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
import asyncio

from settings import RPC_LIST, HEADER
from spider.meta import Spider
from utils.conf import Net, Vm, Module
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
        return {'res': await self.fetch(req), 'task': f'tx.{mode}'}


async def main():
    spider = TransactionSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.TX
    )
    res = await spider.get(mode='trace', hash='0x2f13d202c301c8c1787469310a2671c8b57837eb7a8a768df857cbc7b3ea32d8')
    print(res)

# asyncio.get_event_loop().run_until_complete(main())


