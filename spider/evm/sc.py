#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sc.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
import asyncio
from queue import Queue
from typing import List

import aiohttp

from dao.meta import JsonDao
from item.evm.sc import ABI
from settings import RPC_LIST, HEADER
from spider.meta import Spider, check_item_exists, preprocess_keys, save_item
from utils.conf import Net, Vm, Module
from utils.pc import Job, PC
from utils.req import Request, Headers, Url


class ContractSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.rpc = RPC_LIST.get(self.vm).get(self.module)

    async def get(self, **kwargs):
        mode = kwargs.get('mode')
        address = kwargs.get('address')

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
        res = await self.fetch(req)
        if res is not None:
            return {'res': {'address': address, 'abi': res}, 'task': f'sc.{mode}'}

        return {'res': None, 'task': f'sc.{mode}'}

    @save_item
    @check_item_exists
    @preprocess_keys
    async def crawl(self, keys: List[str], mode: str, out: str):
        source = Queue()
        for address in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'address': address},
                    item={'abi': ABI()}[mode],
                    dao=JsonDao(f"{out}/{address}/{mode}.json")
                )
            )
        pc = PC(source)
        await pc.run()
        queue = [{'key': job.id.split('-')[1], 'item': job.item.dict()} for job in list(pc.fi_q)]
        queue += [{'key': job.id.split('-')[1], 'item': None} for job in list(pc.fa_q)]

        return queue


async def main():
    spider = ContractSpider(
        vm=Vm.EVM,
        net=Net.ETH,
        module=Module.SC
    )
    res = await spider.get(mode='abi', address='0x609c690e8F7D68a59885c9132e812eEbDaAf0c9e')
    print(res)

# asyncio.get_event_loop().run_until_complete(main())




