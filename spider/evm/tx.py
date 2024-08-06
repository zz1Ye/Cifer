from item.evm.tx import Transaction, Trace, Receipt
from settings import HEADER
from spider.meta import Spider
from utils.conf import Net, Vm, Module, Mode
from utils.req import Request, Headers, Result


# class TransactionSpider(Spider):
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         super().__init__(vm, net, module)
#
#     async def get(self, **kwargs) -> Result:
#         mode = kwargs.get('mode')
#         hash = kwargs.get('key')
#
#         if mode not in [Mode.TRANS, Mode.TRACE, Mode.RCPT]:
#             raise ValueError()
#
#         payload = self.rpc.get(mode.value).get("payload")
#         payload["params"] = [hash]
#         req = Request(
#             url=self.provider.get(),
#             method=self.rpc.get(mode.value).get("method"),
#             headers=Headers(
#                 accept=HEADER.get("accept"),
#                 content_type=HEADER.get("content-type"),
#                 user_agents=HEADER.get("user-agents"),
#             ).get(),
#             payload=payload
#         )
#         res = await self.fetch(req)
#         return Result(
#             key=hash,
#             item={
#                 Mode.TRANS: Transaction().map(res),
#                 Mode.TRACE: Trace().map({'array': res}),
#                 Mode.RCPT: Receipt().map(res)
#             }.get(mode) if res is not None else None
#         )
#
#     @save_item
#     @load_exists_item
#     @preprocess_keys
#     async def crawl(self, keys: List[str], mode: Mode, out: str) -> ResultQueue:
#         source = Queue()
#         for hash in keys:
#             source.put(
#                 Job(
#                     spider=self,
#                     params={'mode': mode, 'key': hash, 'id': hash},
#                     dao=JsonDao(self.dir_path(out, hash, mode))
#                 )
#             )
#         pc = PC(source)
#         await pc.run()
#         queue = ResultQueue()
#         while pc.fi_q.qsize() != 0:
#             queue.add(pc.fi_q.get())
#         return queue

class TransactionSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.TX, Mode.TRANS)

    async def parse(self, **kwargs):
        key = kwargs.get('id')
        hash = kwargs.get('hash')

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
        return Result(
            key=key, item=Transaction().map(res).dict()
            if res is not None else {}
        )


class TraceSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.TX, Mode.TRACE)

    async def parse(self, **kwargs):
        key = kwargs.get('id')
        hash = kwargs.get('hash')

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
        return Result(
            key=key, item=Trace().map({'array': res}).dict()
            if res is not None else {}
        )


class ReceiptSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.TX, Mode.RCPT)

    async def parse(self, **kwargs):
        key = kwargs.get('id')
        hash = kwargs.get('hash')

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
        return Result(
            key=key, item=Receipt().map(res).dict()
            if res is not None else {}
        )