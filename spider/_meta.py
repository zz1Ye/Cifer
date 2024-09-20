import json
from abc import ABC, abstractmethod
from typing import List, Union, Dict

import aiohttp
from aiohttp_retry import RetryClient, RandomRetry
from web3 import Web3

from settings import RPC, URL
from utils.conf import Vm, Net
from utils.req import RPCNode


class Param:
    def __init__(self, query: dict, out: str = ""):
        if not isinstance(query, dict):
            raise TypeError()
        self.id = '_'.join(str(v) for k, v in sorted(query.items()))
        self.query = query
        self.out = out if out != "" else f"out/"


class Result:
    def __init__(self, key, item: dict):
        self.key = key
        self.item = item


class Crawlable(ABC):
    def __init__(self, vm: Vm, net: Net):
        self.vm, self.net = vm, net
        self.module, self.mode = None, None
        self.url = URL.get(self.vm.value, {}).get(self.net.value, {})
        self.provider = RPCNode(
            domain=self.url.get("provider", {}).get("domain"),
            keys=self.url.get("provider", {}).get("keys"),
        )

    async def crawl(self, params: Union[Param, List[Param]]) -> List[Result]:
        if isinstance(params, dict):
            params = [params]
        return await self.parse(params)

    @abstractmethod
    async def parse(self, params: List[Param]) -> List[Result]:
        raise NotImplementedError("Subclasses must implement this method.")


class Spider(Crawlable):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.scan = RPCNode(
            domain=self.url.get("scan", {}).get("domain"),
            keys=self.url.get("scan", {}).get("keys"),
        )
        self.rpc = RPC.get(self.vm.value, {})

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

    @abstractmethod
    async def parse(self, params: List[Param]) -> List[Result]:
        raise NotImplementedError("Subclasses must implement this method.")


class Parser(Crawlable):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.w3 = Web3(Web3.HTTPProvider(
            self.provider.get()
        ))

    @abstractmethod
    async def parse(self, params: List[Param]) -> List[Result]:
        raise NotImplementedError("Subclasses must implement this method.")


