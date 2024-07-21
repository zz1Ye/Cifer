#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sc.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
from queue import Queue
from typing import List

from dao.meta import JsonDao
from item.evm.sc import ABI
from settings import HEADER
from spider.meta import Spider, preprocess_keys, save_item, load_exists_item, Result, ResultQueue
from utils.conf import Net, Vm, Module, Mode
from utils.pc import Job, PC
from utils.req import Request, Headers, Url


class ContractSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get(self, **kwargs) -> Result:
        mode = kwargs.get('mode')
        address = kwargs.get('key')

        if mode not in [Mode.ABI]:
            raise ValueError()
        params = {
            'module': self.rpc.get(mode.value).get("params").get("module"),
            'action': self.rpc.get(mode.value).get("params").get("action"),
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
        return Result(
            key=address,
            item={
                Mode.ABI: ABI().map({'address': address, 'abi': res})
            }.get(mode) if res not in [
                None, 'Contract source code not verified',
                'Max rate limit reached'
            ] else None
        )

    @save_item
    @load_exists_item
    @preprocess_keys
    async def crawl(self, keys: List[str], mode: Mode, out: str) -> ResultQueue:
        source = Queue()
        for address in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'key': address},
                    dao=JsonDao(self.dir_path(out, address, mode))
                )
            )
        pc = PC(source)
        await pc.run()
        queue = ResultQueue()
        while pc.fi_q.qsize() != 0:
            queue.add(pc.fi_q.get())

        return queue
