#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ts.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
from queue import Queue
from typing import List

from dao.meta import JsonDao
from item.evm.tx import Transaction, Trace, Receipt
from settings import HEADER
from spider.meta import Spider, check_item_exists, preprocess_keys, save_item
from utils.conf import Net, Vm, Module, Mode
from utils.pc import Job, PC
from utils.req import Request, Headers


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get(self, **kwargs):
        mode = kwargs.get('mode')
        hash = kwargs.get('key')

        if mode not in [Mode.TRANS, Mode.TRACE, Mode.RCPT]:
            raise ValueError()

        payload = self.rpc.get(mode.value).get("payload")
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
        if mode == Mode.TRACE:
            return {'res': res if res is None else {'array': res}}
        return {'res': res}

    @save_item
    @check_item_exists
    @preprocess_keys
    async def crawl(self, keys: List[str], mode: Mode, out: str):
        source = Queue()
        for hash in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'key': hash},
                    item={
                        Mode.TRANS: Transaction(),
                        Mode.TRACE: Trace(), Mode.RCPT: Receipt()
                    }[mode],
                    dao=JsonDao(self.dir_path(out, hash, mode))
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



