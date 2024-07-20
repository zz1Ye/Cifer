import json
from functools import wraps
from typing import List

import aiohttp
from aiohttp_retry import RetryClient, RandomRetry

from dao.meta import JsonDao
from settings import URL_DICT, RPC_LIST
from utils.conf import Net, Vm, Module, Mode
from utils.req import RPCNode


def preprocess_keys(func):
    @wraps(func)
    def wrapper(self, keys: List[str], mode: Mode, out: str):
        n_keys = list(set([k.lower() for k in keys]))
        return func(self, n_keys, mode, out)

    return wrapper


def load_exists_item(func):
    @wraps(func)
    async def wrapper(self, keys: List[str], mode: Mode, out: str):
        n_keys = set([
            k for k in keys
            if not JsonDao(self.dir_path(out, k, mode)).exist()
        ])
        item_dict = {}
        for k in set(keys) - n_keys:
            dao = JsonDao(self.dir_path(out, k, mode))
            item = [e for e in dao.load()][0][0]
            item_dict[k] = {'key': k, 'item': item}

        for e in await func(self, list(n_keys), mode, out):
            key, item = e.get("key"), e.get("item")
            item_dict[k] = {'key': key, 'item': item}

        queue = [item_dict[k] for k in keys]
        return queue
    return wrapper


def save_item(func):
    @wraps(func)
    async def wrapper(self, keys: List[str], mode: Mode, out: str):
        queue = await func(self, keys, mode, out)
        for e in queue:
            key, item = e.get("key"), e.get("item")
            if item is not None:
                dao = JsonDao(self.dir_path(out, key, mode))
                if not dao.exist():
                    dao.create()
                    dao.insert(item)
        return queue

    return wrapper


class Meta:
    def __init__(self, vm: Vm, net: Net, module: Module):
        self.vm = vm
        self.net = net
        self.module = module
        url_dict = URL_DICT.get(self.vm.value, {}).get(self.net.value, {})

        self.scan = RPCNode(
            domain=url_dict.get("scan", {}).get("domain"),
            keys=url_dict.get("scan", {}).get("keys"),
        )
        self.provider = RPCNode(
            domain=url_dict.get("provider", {}).get("domain"),
            keys=url_dict.get("provider", {}).get("keys"),
        )
        self.rpc = RPC_LIST.get(self.vm.value, {}).get(self.module.value)
        self._id = '{}_{}_{}'.format(
            self.vm, self.net, self.module
        )

    def dir_path(self, out: str, key: str, mode: Mode):
        return '{}/{}/{}/{}/{}/{}.json'.format(
            out, self.vm.value, self.net.value,
            self.module.value, key, mode.value
        )

    @property
    def id(self):
        return self._id


class Spider(Meta):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

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


class Parser(Meta):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def parse(self, keys: List[str], mode: Mode, out: str):
        raise NotImplementedError()

