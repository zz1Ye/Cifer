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
from spider.meta import Spider, preprocess_keys, save_item, load_exists_item, Result, ResultQueue
from utils.conf import Net, Vm, Module, Mode
from utils.pc import Job, PC
from utils.req import Request, Headers


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get(self, **kwargs) -> Result:
        mode = kwargs.get('mode')
        hash = kwargs.get('key')

        if mode not in [Mode.TRANS, Mode.TRACE, Mode.RCPT]:
            raise ValueError()

        payload = self.rpc.get(mode.value).get("payload")
        payload["params"] = [hash]
        req = Request(
            url=self.provider.get(),
            method=self.rpc.get(mode.value).get("method"),
            headers=Headers(
                accept=HEADER.get("accept"),
                content_type=HEADER.get("content-type"),
                user_agents=HEADER.get("user-agents"),
            ).get(),
            payload=payload
        )
        res = await self.fetch(req)
        return Result(
            key=hash,
            item={
                Mode.TRANS: Transaction().map(res),
                Mode.TRACE: Trace().map({'array': res}),
                Mode.RCPT: Receipt().map(res)
            }.get(mode) if res is not None else None
        )

        # if mode == Mode.TRACE:
        #     return {'res': res if res is None else {'array': res}}
        # return {'res': res}

    @save_item
    @load_exists_item
    @preprocess_keys
    async def crawl(self, keys: List[str], mode: Mode, out: str) -> ResultQueue:
        source = Queue()
        for hash in keys:
            source.put(
                Job(
                    spider=self,
                    params={'mode': mode, 'key': hash},
                    dao=JsonDao(self.dir_path(out, hash, mode))
                )
            )
        pc = PC(source)
        await pc.run()
        queue = ResultQueue()
        while pc.fi_q.qsize() != 0:
            queue.add(pc.fi_q.get())

        return queue



