from item.evm.sc import ABI
from settings import HEADER
from spider.meta import Spider, Result
from utils.conf import Net, Vm, Module, Mode
from utils.req import Request, Headers, Url


class ContractSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get(self, **kwargs) -> Result:
        mode = kwargs.get('mode')
        address = kwargs.get('key')

        if mode not in [Mode.ABI]:
            raise ValueError()
        params = {
            'module': self.rpc.get(mode.value).get("params").get("module"),
            'action': self.rpc.get(mode.value).get("params").get("action"),
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
        return Result(
            key=address,
            item={
                Mode.ABI: ABI().map({'address': address, 'abi': res})
            }.get(mode) if res not in [
                None, 'Contract source code not verified',
                'Max rate limit reached'
            ] else None
        )
