#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : tx.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
from spider._meta import Spider
from utils.conf import Net, Vm, Module


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get_trans(self, hash: str):
        rpc = self.rpc.get("trans")
        rpc["url"] = self.providers[0]
        rpc["params"] = [hash]

        return await self.fetch(rpc)

    async def get_trace(self, hash: str):
        rpc = self.rpc.get("trace")
        rpc["url"] = self.providers[0]
        rpc["params"] = [hash]

        return await self.fetch(rpc)

    async def get_rcpt(self, hash: str):
        rpc = self.rpc.get("rcpt")
        rpc["url"] = self.providers[0]
        rpc["params"] = [hash]

        return await self.fetch(rpc)


