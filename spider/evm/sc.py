#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sc.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
import asyncio

import aiohttp

from settings import RPC_LIST, HEADER
from spider._meta import Spider
from utils.conf import Net, Vm, Module
from utils.req import Request, Headers, Url


class ContractSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.rpc = RPC_LIST.get(self.vm).get(self.module)

    async def get(self, mode: str, address: str):
        if mode not in ["abi"]:
            raise ValueError()

        params = {
            'module': self.rpc.get(mode).get("params").get("module"),
            'action': self.rpc.get(mode).get("params").get("action"),
            'address': address,
            'apikey': self.scan.get_key()
        }
        req = Request(
            url=Url(domain=self.scan.domain, params=params).get(),
            method="GET",
            headers=Headers(
                accept=HEADER.get("accept"),
                content_type=HEADER.get("content-type"),
                user_agents=HEADER.get("user-agents"),
            ).get(),
            payload={}
        )
        return {'res': await self.fetch(req), 'task': f'sc.{mode}'}


async def main():
    spider = ContractSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.SC
    )
    res = await spider.get(mode='abi', address='0x609c690e8F7D68a59885c9132e812eEbDaAf0c9e')
    print(res)

# asyncio.get_event_loop().run_until_complete(main())




