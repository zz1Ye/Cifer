#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : blk.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
from queue import Queue
from typing import List

from dao.meta import JsonDao
from item.evm.blk import Block
from settings import RPC_LIST, HEADER
from spider.meta import Spider, check_item_exists
from utils.conf import Vm, Net, Module
from utils.pc import Job, PC
from utils.req import Request, Headers


class BlockSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.rpc = RPC_LIST.get(self.vm).get(self.module)

    async def get(self, **kwargs):
        mode = kwargs.get('mode')
        hash = kwargs.get('hash')

        if mode not in ["block"]:
            raise ValueError()

        payload = self.rpc.get(mode).get("payload")
        payload["params"] = [hash, True]

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
        return {'res': await self.fetch(req), 'task': f'blk.{mode}'}

    @check_item_exists
    async def crawl(self, keys: List[str], mode: str, out: str):
        source = Queue()
        for hash in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'hash': hash},
                    item={'abi': Block()}[mode],
                    dao=JsonDao(f"{out}/{hash}/{mode}.json")
                )
            )
        pc = PC(source)
        await pc.run()
        return list(pc.fi_q), list(pc.fa_q)

