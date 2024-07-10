#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : _meta.py
@Time   : 2024/7/9 12:42
@Author : zzYe

"""
import json

import aiohttp

from settings import APIS, PROVIDERS, API_KEYS, RPCS
from utils.conf import Net, Vm, Module


class Spider:
    def __init__(self, vm: Vm, net: Net, module: Module):
        self.vm = vm
        self.net = net
        self.module = module
        self.rpc = RPCS.get(vm).get(module)
        self.api = APIS.get(self.net)
        self.api_keys = API_KEYS.get(self.net)
        self.providers = PROVIDERS.get(self.net)

    @staticmethod
    async def fetch(rpc):
        url, method = rpc.get("url"), rpc.get("method")
        headers, payload = rpc.get("headers"), rpc.get("payload")

        async with aiohttp.ClientSession() as session:
            if method.upper() == 'GET':
                async with session.get(
                    url, headers=headers
                ) as response:
                    content = await response.text()
            elif method.upper() == 'POST':
                async with session.post(
                    url, headers=headers, data=json.dumps(payload)
                ) as response:
                    content = await response.text()
            else:
                raise ValueError("Unsupported HTTP method: " + method)

            return content

