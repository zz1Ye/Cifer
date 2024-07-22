import json
from functools import wraps
from queue import Queue
from typing import List

import aiohttp
from aiohttp_retry import RetryClient, RandomRetry

from dao.meta import JsonDao
from item.meta import Item
from settings import URL, RPC
from utils.conf import Net, Vm, Module, Mode
from utils.pc import Job, PC
from utils.req import RPCNode


class Result:
    def __init__(self, key, item: Item = None):
        self.key = key
        self.item = item


class ResultQueue:
    def __init__(self, queue: List[Result] = None):
        if queue is None:
            queue = []
        self.queue = queue
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.queue):
            result = self.queue[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.queue[index]

    def __setitem__(self, index, value):
        self.queue[index] = value

    def __len__(self):
        return len(self.queue)

    def add(self, element: Result):
        self.queue.append(element)

    def get_none_idx(self):
        return [
            i
            for i, e in enumerate(self.queue)
            if e.item is None
        ]

    def get_non_none_idx(self):
        return [
            i
            for i, e in enumerate(self.queue)
            if e.item is not None
        ]


def preprocess_keys(func):
    @wraps(func)
    def wrapper(self, keys: List[str], mode: Mode, out: str):
        n_keys = [k.lower() for k in keys]
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
            item_dict[k] = Result(key=k, item=mode.new_mapping_item().map(item))

        for e in await func(self, list(n_keys), mode, out):
            item_dict[e.get("key")] = e

        return ResultQueue(queue=[item_dict[k] for k in keys])
    return wrapper


def save_item(func):
    @wraps(func)
    async def wrapper(self, keys: List[str], mode: Mode, out: str):
        queue = await func(self, keys, mode, out)
        for e in queue:
            key, item = e.key, e.item
            if item is not None:
                dao = JsonDao(self.dir_path(out, key, mode))
                if not dao.exist():
                    dao.create()
                    dao.insert(item.dict())
        return queue

    return wrapper


class Meta:
    def __init__(self, vm: Vm, net: Net, module: Module):
        self.vm = vm
        self.net = net
        self.module = module
        url = URL.get(self.vm.value, {}).get(self.net.value, {})

        self.scan = RPCNode(
            domain=url.get("scan", {}).get("domain"),
            keys=url.get("scan", {}).get("keys"),
        )
        self.provider = RPCNode(
            domain=url.get("provider", {}).get("domain"),
            keys=url.get("provider", {}).get("keys"),
        )
        self.rpc = RPC.get(self.vm.value, {}).get(self.module.value)
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

    async def get(self, **kwargs) -> Result:
        raise NotImplementedError()

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

    async def parse(self, keys: List[str], mode: Mode, out: str) -> ResultQueue:
        raise NotImplementedError()

