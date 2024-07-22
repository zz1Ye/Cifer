from item.evm.blk import Block
from settings import HEADER
from spider.meta import Spider, Result
from utils.conf import Vm, Net, Module, Mode
from utils.req import Request, Headers


class BlockSpider(Spider):
    def __init__(self, vm: Vm, net: Net, module: Module):
        super().__init__(vm, net, module)

    async def get(self, **kwargs) -> Result:
        mode = kwargs.get('mode')
        hash = kwargs.get('key')

        if mode not in [Mode.BLOCK]:
            raise ValueError()

        payload = self.rpc.get(mode.value).get("payload")
        payload["params"] = [hash, True]

        req = Request(
            url=self.provider.get(),
            method=self.rpc.get(mode.value).get("method"),
            headers=Headers(
                accept=HEADER.get("accept"),
                content_type=HEADER.get("content-type"),
                user_agents=HEADER.get("user-agents"),
            ).get(),
            payload=payload
        )
        res = await self.fetch(req)
        return Result(
            key=hash,
            item={
                Mode.BLOCK: Block().map(res)
            }.get(mode) if res is not None else None
        )
