import asyncio
import json
import logging
from enum import Enum
from functools import wraps
from queue import Queue
from typing import List

import aiohttp
from aiohttp_retry import RetryClient, RandomRetry
from pybloom import BloomFilter

from dao.meta import JsonDao, Dao
from settings import URL, RPC
from utils.conf import Net, Vm, Module, Mode
from utils.req import RPCNode, Result, ResultQueue


def create_ids(func):
    @wraps(func)
    def wrapper(self, params: List[dict]):
        params = [
            {
                **{
                    k: v.lower() if isinstance(v, str) else v
                    for k, v in e.items()
                },
                'id': '_'.join(str(v) for k, v in sorted(e.items()) if k not in ['out'])
            }
            for e in params
        ]
        return func(self, params)
    return wrapper

#
# def preprocess_keys(func):
#     @wraps(func)
#     def wrapper(self, keys: List[str], mode: Mode, out: str):
#         n_keys = [k.lower() for k in keys]
#         return func(self, n_keys, mode, out)
#
#     return wrapper


def load_exists_item(func):
    @wraps(func)
    async def wrapper(self, params: List[dict]):
        out_dict = {e['id']: e.get('out') for e in params}
        done = set([
            e['id'] for e in params
            if JsonDao(self.dir_path(e.get('out'), e.get('id'))).exist()
        ])

        undone = set([
            e['id'] for e in params
            if not JsonDao(self.dir_path(e.get('out'), e.get('id'))).exist()
        ])

        item_dict = {}
        for _id in done:
            dao = JsonDao(self.dir_path(out_dict[_id], _id))
            item = [e for e in dao.load()][0][0]
            item_dict[_id] = Result(key=_id, item=item)

        undone_params = [e for e in params if e.get("id") in undone]
        for e in await func(self, undone_params):
            item_dict[e.key] = e

        return ResultQueue(queue=[item_dict[e['id']] for e in params])
    return wrapper


def save_item(func):
    @wraps(func)
    async def wrapper(self, params: List[dict]):
        out_dict = {e['id']: e.get('out') for e in params}

        queue = await func(self, params)
        for e in queue:
            key, item = e.key, e.item
            if len(item) != 0:
                dao = JsonDao(self.dir_path(out_dict[key], key))
                if not dao.exist():
                    dao.create()
                    dao.insert(item)
        return queue
    return wrapper


class Spider:
    def __init__(self, vm: Vm, net: Net, module: Module, mode: Mode):
        self.vm, self.net = vm, net
        self.module, self.mode = module, mode
        url_dict = URL.get(self.vm.value, {}).get(self.net.value, {})

        self.scan = RPCNode(
            domain=url_dict.get("scan", {}).get("domain"),
            keys=url_dict.get("scan", {}).get("keys"),
        )
        self.provider = RPCNode(
            domain=url_dict.get("provider", {}).get("domain"),
            keys=url_dict.get("provider", {}).get("keys"),
        )
        self.rpc = RPC.get(self.vm.value, {}).get(self.module.value, {}).get(self.mode.value, {})
        self._id = '{}_{}_{}'.format(
            self.vm, self.net, self.module
        )

    def dir_path(self, out: str, id: str):
        return '{}/{}/{}/{}/{}/{}.json'.format(
            out, self.vm.value, self.net.value,
            self.module.value, id, self.mode.value
        )

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

    async def parse(self, **kwargs):
        raise NotImplementedError()

    @create_ids
    @load_exists_item
    @save_item
    async def crawl(self, params: List[dict]) -> ResultQueue:
        source = Queue()
        for e in params:
            source.put(Job(
                spider=self, param=e,
                dao=JsonDao(self.dir_path(e.get('out'), e.get('id')))
            ))
        pc = PC(source)
        await pc.run()
        queue = ResultQueue()
        while pc.fi_q.qsize() != 0:
            queue.add(pc.fi_q.get())
        return queue

    # async def get(self, **kwargs) -> Result:
    #     raise NotImplementedError()

# class Meta:
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         self.vm = vm
#         self.net = net
#         self.module = module
#         url = URL.get(self.vm.value, {}).get(self.net.value, {})
#
#         self.scan = RPCNode(
#             domain=url.get("scan", {}).get("domain"),
#             keys=url.get("scan", {}).get("keys"),
#         )
#         self.provider = RPCNode(
#             domain=url.get("provider", {}).get("domain"),
#             keys=url.get("provider", {}).get("keys"),
#         )
#         self.rpc = RPC.get(self.vm.value, {}).get(self.module.value)
#         self._id = '{}_{}_{}'.format(
#             self.vm, self.net, self.module
#         )
#
#     def dir_path(self, out: str, key: str, mode: Mode):
#         return '{}/{}/{}/{}/{}/{}.json'.format(
#             out, self.vm.value, self.net.value,
#             self.module.value, key, mode.value
#         )
#
#     @property
#     def id(self):
#         return self._id


# class Parser(Meta):
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         super().__init__(vm, net, module)
#
#     async def parse(self, keys: List[str], mode: Mode, out: str) -> ResultQueue:
#         raise NotImplementedError()


class Status(Enum):
    READY = 'ready'
    RUNNING = 'running'
    FINISHED = 'finished'


class Job:
    def __init__(
            self, spider: Spider,
            param: dict, dao: Dao
    ):
        self.spider = spider
        self.param = param
        self.id = param.get('id')
        self.res = Result(key=self.id, item={})
        self.dao = dao
        self.status = Status.READY

    async def run(self):
        self.status = Status.RUNNING
        try:
            self.res = await self.spider.parse(**self.param)
        except (
            NotImplementedError, ValueError, asyncio.exceptions.TimeoutError,
            aiohttp.client_exceptions.ClientPayloadError
        ) as e:
            logging.error(e)
        self.status = Status.FINISHED


class PC:
    def __init__(self, source: Queue[Job], cp_ratio: int = 2, maxsize: int = 8):
        """
        Three queue: Ready/Running/Finished
        """
        self.re_q = Queue()
        self.ru_q = asyncio.Queue(maxsize=maxsize)
        self.fi_q = Queue()

        if not(isinstance(cp_ratio, int) and cp_ratio >= 1):
            raise ValueError()
        self.cp_ratio = cp_ratio

        self.bf = BloomFilter(capacity=1_000_000, error_rate=0.001)
        self.wl, self.el = set(), set()

        while not source.empty():
            job = source.get()
            if job.id not in self.bf:
                self.re_q.put(job)
                self.bf.add(job.id)
                continue

            if job.id not in self.wl:
                self.re_q.put(job)
                self.wl.add(job.id)

        self._status = Status.READY
        self._count = 0

    async def producer(self):
        while self.re_q.qsize() != 0:
            job = self.re_q.get()
            await self.ru_q.put(job)

    async def consumer(self):
        while not (self.re_q.qsize() == 0 and self.ru_q.qsize() == 0):
            job = await self.ru_q.get()
            await job.run()
            assert job.status == Status.FINISHED
            self.fi_q.put(job.res)
            self._count += 1

            if self._count % 1000 == 0:
                print(
                    f"The current count of completed jobs is: "
                    f"{self._count}."
                )

    async def run(self):
        self._status = Status.RUNNING
        print(
            f"Start executing, the total number of jobs is: "
            f"{self.re_q.qsize()}."
        )

        p_worker = asyncio.create_task(self.producer())
        c_workers = [
            asyncio.create_task(self.consumer())
            for _ in range(self.cp_ratio)
        ]
        workers = [p_worker] + c_workers
        await asyncio.gather(*workers)
        print(
            f"The current count of completed jobs is: "
            f"{self._count}."
        )
        self._status = Status.FINISHED

