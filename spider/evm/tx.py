#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : tx.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
from settings import RPC_LIST, HEADER
from spider._meta import Spider
from utils.conf import Net, Vm, Module
from utils.req import Request, Headers


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)
        self.rpc = RPC_LIST.get(self.vm).get(self.module)

    async def get(self, mode: str, hash: str):
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
        return await self.fetch(req)



