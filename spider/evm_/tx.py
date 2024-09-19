from typing import List, Dict

from item.evm.tx import Transaction, Trace, Receipt
from settings import HEADER
from spider._meta import Spider
from utils.conf import Net, Vm, Module, Mode
from utils.req import Request, Headers, Result


class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.TX, Mode.TRANS
        self.rpc = self.rpc.get(self.module.value, {}).get(self.mode.value, {})

    async def parse(self, params: List[Dict]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.get('id'), p.get('hash')
            payload = self.rpc.get("payload")
            payload["params"] = [hash]
            req = Request(
                url=self.provider.get(),
                method=self.rpc.get("method"),
                headers=Headers(
                    accept=HEADER.get("accept"),
                    content_type=HEADER.get("content-type"),
                    user_agents=HEADER.get("user-agents"),
                ).get(),
                payload=payload
            )
            res = await self.fetch(req)
            res_arr.append(
                Result(
                    key=key, item=Transaction().map(res).dict()
                    if res is not None else {}
                )
            )
        return res_arr


class TraceSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.TX, Mode.TRACE
        self.rpc = self.rpc.get(self.module.value, {}).get(self.mode.value, {})

    async def parse(self, params: List[Dict]) -> List[Result]:
        res_arr = []
        for p in params:
            key = p.get('id')
            hash = p.get('hash')
            payload = self.rpc.get("payload")
            payload["params"] = [hash]
            req = Request(
                url=self.provider.get(),
                method=self.rpc.get("method"),
                headers=Headers(
                    accept=HEADER.get("accept"),
                    content_type=HEADER.get("content-type"),
                    user_agents=HEADER.get("user-agents"),
                ).get(),
                payload=payload
            )
            res = await self.fetch(req)
            res_arr.append(
                Result(
                    key=key, item=Trace().map({'array': res}).dict()
                    if res is not None else {}
                )
            )
        return res_arr


class ReceiptSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.TX, Mode.RCPT
        self.rpc = self.rpc.get(self.module.value, {}).get(self.mode.value, {})

    async def parse(self, params: List[Dict]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.get('id'), p.get('hash')
            payload = self.rpc.get("payload")
            payload["params"] = [hash]
            req = Request(
                url=self.provider.get(),
                method=self.rpc.get("method"),
                headers=Headers(
                    accept=HEADER.get("accept"),
                    content_type=HEADER.get("content-type"),
                    user_agents=HEADER.get("user-agents"),
                ).get(),
                payload=payload
            )
            res = await self.fetch(req)
            res_arr.append(
                Result(
                    key=key, item=Receipt().map(res).dict()
                    if res is not None else {}
                )
            )
        return res_arr
