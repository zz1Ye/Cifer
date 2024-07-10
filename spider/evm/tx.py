#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : tx.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
from settings import RPCS
from spider._meta import Spider
from utils.conf import Net, Vm, Module


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get_trans(self, hash: str):
        TARGET = "trans"
        rpc = self.rpc.get(TARGET)

        url = self.domain
        headers = self.rpc.get(TARGET).get("headers")
        payload = self.rpc.get(TARGET).get("payload")
        payload["params"] = [hash]
        method = self.rpc.get(TARGET).get("method")

        return await self.fetch(url, method, headers, payload)

    async def get_trace(self, hash: str):
        TARGET = "trace"


