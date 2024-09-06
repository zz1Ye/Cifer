from item.evm.blk import Block
from settings import HEADER
from spider.meta import Spider, Result
from utils.conf import Vm, Net, Module, Mode
from utils.req import Request, Headers


class BlockSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.BLK, Mode.BLOCK)

    async def parse(self, **kwargs):
        key = kwargs.get('id')
        hash = kwargs.get('hash')

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
        return Result(
            key=key, item=Block().map(res).dict()
            if res is not None else {}
        )

    # @save_item
    # @load_exists_item
    # @preprocess_keys
    # async def crawl(self, keys: List[str], mode: Mode, out: str) -> ResultQueue:
    #     source = Queue()
    #     for hash in keys:
    #         source.put(
    #             Job(
    #                 spider=self,
    #                 params={'mode': mode, 'key': hash, 'id': hash},
    #                 dao=JsonDao(self.dir_path(out, hash, mode))
    #             )
    #         )
    #     pc = PC(source)
    #     await pc.run()
    #     queue = ResultQueue()
    #     while pc.fi_q.qsize() != 0:
    #         queue.add(pc.fi_q.get())
    #     return queue
