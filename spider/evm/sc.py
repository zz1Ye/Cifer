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
from spider.meta import Spider, preprocess_keys, save_item, load_exists_item
from utils.conf import Net, Vm, Module, Mode
from utils.pc import Job, PC
from utils.req import Request, Headers, Url


class ContractSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get(self, **kwargs):
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
        if res is None or res == 'Contract source code not verified':
            return {'res': None}

        return {'res': {'address': address, 'abi': res}}

    @save_item
    @load_exists_item
    @preprocess_keys
    async def crawl(self, keys: List[str], mode: Mode, out: str):
        source = Queue()
        for address in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'key': address},
                    item={Mode.ABI: ABI()}[mode],
                    dao=JsonDao(self.dir_path(out, address, mode))
                )
            )
        pc = PC(source)
        await pc.run()
        queue = []
        while pc.fi_q.qsize() != 0:
            job = pc.fi_q.get()
            queue.append({'key': job.id.split('-')[1], 'item': job.item.dict()})
        while pc.fa_q.qsize() != 0:
            job = pc.fa_q.get()
            queue.append({'key': job.id.split('-')[1], 'item': None})

        return queue




