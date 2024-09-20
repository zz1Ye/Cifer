from typing import List, Dict

from item.evm.blk import Block
from settings import HEADER
from spider._meta import Spider, Result, Param
from utils.conf import Vm, Net, Module, Mode
from utils.req import Request, Headers


class BlockSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.BLK, Mode.BLOCK
        self.rpc = self.rpc.get(self.module.value, {}).get(self.mode.value, {})

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for p in params:
            key, hash = p.id, p.query.get('hash')
            payload = self.rpc.get("payload")
            payload["params"] = [hash, True]

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
                    key=key, item=Block().map(res).dict()
                    if res is not None else {}
                )
            )
        return res_arr
