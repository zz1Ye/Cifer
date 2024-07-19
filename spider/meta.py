#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : meta.py
@Time   : 2024/7/9 12:42
@Author : zzYe

"""
import json
from functools import wraps
from typing import List

import aiohttp
from aiohttp_retry import RetryClient, RandomRetry

from dao.meta import JsonDao
from settings import URL_DICT
from utils.conf import Net, Vm, Module
from utils.req import RPCNode


def preprocess_keys(func):
    @wraps(func)
    def wrapper(self, keys: List[str], mode: str, out: str):
        n_keys = list(set([k.lower() for k in keys]))
        return func(self, n_keys, mode, out)

    return wrapper


def check_item_exists(func):
    @wraps(func)
    def wrapper(self, keys: List[str], mode: str, out: str):
        n_keys = [
            k for k in keys
            if not JsonDao(f'{out}/{k}/{mode}.json').exist()
        ]
        return func(self, n_keys, mode, out)
    return wrapper


def save_item(func):
    @wraps(func)
    async def wrapper(self, keys: List[str], mode: str, out: str):
        queue = await func(self, keys, mode, out)

        for e in queue:
            key, item = e.get("key"), e.get("item")
            if item is not None:
                dao = JsonDao(f'{out}/{key}/{mode}.json')
                dao.create()
                dao.insert(item)
        return queue

    return wrapper


class Spider:
    def __init__(self, vm: Vm, net: Net, module: Module):
        self.vm = vm.value
        self.net = net.value
        self.module = module.value
        self.scan = RPCNode(
            domain=URL_DICT.get(self.vm).get(self.net).get("scan").get("domain"),
            keys=URL_DICT.get(self.vm).get(self.net).get("scan").get("keys"),
        )
        self.provider = RPCNode(
            domain=URL_DICT.get(self.vm).get(self.net).get("provider").get("domain"),
            keys=URL_DICT.get(self.vm).get(self.net).get("provider").get("keys"),
        )
        self._id = '{}_{}_{}'.format(
            self.vm, self.net, self.module,
            self.__class__.__qualname__
        )

    @property
    def id(self):
        return self._id

    def get(self, **kwargs):
        raise NotImplementedError()

    async def crawl(self, keys: List[str], mode: str, out: str):
        raise NotImplementedError()

    @staticmethod
    async def fetch(req, retries: int = 3):
        req = req.dict()
        url, method = req.get("url"), req.get("method")
        headers, payload = req.get("headers"), req.get("payload")

        async with RetryClient(
            retry_options=RandomRetry(attempts=retries),
            client_session=aiohttp.ClientSession()
        ) as client:
            if method.upper() == 'GET':
                async with client.get(
                    url, headers=headers
                ) as response:
                    content = await response.json()
            elif method.upper() == 'POST':
                async with client.post(
                        url, headers=headers,
                        data=json.dumps(payload),
                ) as response:
                    content = await response.json()
            else:
                raise ValueError()

        return content.get("result", None)


class Parser:
    def __init__(self, vm: Vm, net: Net, module: Module):
        self.vm = vm.value
        self.net = net.value
        self.module = module.value
        self.scan = RPCNode(
            domain=URL_DICT.get(self.vm).get(self.net).get("scan").get("domain"),
            keys=URL_DICT.get(self.vm).get(self.net).get("scan").get("keys"),
        )
        self.provider = RPCNode(
            domain=URL_DICT.get(self.vm).get(self.net).get("provider").get("domain"),
            keys=URL_DICT.get(self.vm).get(self.net).get("provider").get("keys"),
        )
        self._id = '{}_{}_{}'.format(
            self.vm, self.net, self.module,
            self.__class__.__qualname__
        )

    @property
    def id(self):
        return self._id

    async def parse(self, keys: List[str], mode: str, out: str):
        raise NotImplementedError()

