from typing import List, Dict

from item.evm.ac import ABI
from settings import HEADER
from spider._meta import Spider
from utils.conf import Net, Vm, Module, Mode
from utils.req import Request, Headers, Url, Result


class ABISpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.AC, Mode.ABI
        self.rpc = self.rpc.get(self.module.value, {}).get(self.mode.value, {})

    async def parse(self, params: List[Dict]) -> List[Result]:
        res_arr = []
        for p in params:
            key, address = p.get('id'), p.get('address')
            params = {
                'module': self.rpc.get("params").get("module"),
                'action': self.rpc.get("params").get("action"),
                'address': address,
                'apikey': self.scan.get_key()
            }
            req = Request(
                url=Url(domain=self.scan.domain, params=params).get(),
                method="GET",
                headers=Headers(
                    accept=HEADER.get("accept"),
                    content_type=HEADER.get("content-type"),
                    user_agents=HEADER.get("user-agents"),
                ).get(),
                payload={}
            )
            res = await self.fetch(req)
            res_arr.append(
                Result(
                    key=key,
                    item=ABI().map({'address': address, 'abi': res}).dict()
                    if res not in [
                        None, 'Contract source code not verified',
                        'Max rate limit reached'
                    ] else None
                )
            )
        return res_arr
