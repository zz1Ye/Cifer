import asyncio
import logging

from item.evm.ac import ABI, TxList
from settings import HEADER
from spider.meta import Spider
from utils.conf import Net, Vm, Module, Mode
from utils.req import Request, Headers, Url, Result, ResultQueue


# class AccountSpider(Spider):
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         super().__init__(vm, net, module)
#         self.start_blk = 0
#         self.end_blk = 9999999999
#
#     async def get(self, **kwargs) -> Result:
#         mode = kwargs.get('mode')
#         address = kwargs.get('key')
#
#         if mode not in [Mode.ABI, Mode.TXLIST]:
#             raise ValueError()
#
#         if mode == Mode.ABI:
#             return await self.get_abi(address=address)
#
#         if mode == Mode.TXLIST:
#             return await self.get_txs(address=address, **kwargs)
#
#     async def get_abi(self, address: str):
#         return Result(key=address, item=None)
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
#
#     async def get_txs(self, address: str, **kwargs) -> Result:
#         tasks = [
#             asyncio.create_task(self.get_external_txs(address, **kwargs)),
#             asyncio.create_task(self.get_internal_txs(address, **kwargs)),
#             asyncio.create_task(self.get_erc20_txs(address, **kwargs)),
#             asyncio.create_task(self.get_erc721_txs(address, **kwargs))
#         ]
#         ext_txs, int_txs, erc20_txs, erc721_txs = await asyncio.gather(*tasks)
#         res = ext_txs + int_txs + erc20_txs + erc721_txs
#         return Result(
#             key=address,
#             item=TxList().map({'array': res})
#             if len(res) != 0 else None
#         )
#
#     async def get_external_txs(self, address: str, **kwargs) -> []:
#         params = {
#             'module': 'account',
#             'action': 'txlist',
#             'address': address,
#             'sort': 'asc',
#             'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
#             'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
#             'apikey': self.scan.get_key()
#         }
#
#         req = Request(
#             url=Url(domain=self.scan.domain, params=params).get(),
#             method="GET",
#             headers=Headers(
#                 accept=HEADER.get("accept"),
#                 content_type=HEADER.get("content-type"),
#                 user_agents=HEADER.get("user-agents"),
#             ).get(),
#             payload={}
#         )
#         res = await self.fetch(req)
#         return res if res is not None else []
#
#     async def get_internal_txs(self, address: str, **kwargs) -> ResultQueue:
#         params = {
#             'module': 'account',
#             'action': 'txlistinternal',
#             'address': address,
#             'sort': 'asc',
#             'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
#             'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
#             'apikey': self.scan.get_key()
#         }
#
#         req = Request(
#             url=Url(domain=self.scan.domain, params=params).get(),
#             method="GET",
#             headers=Headers(
#                 accept=HEADER.get("accept"),
#                 content_type=HEADER.get("content-type"),
#                 user_agents=HEADER.get("user-agents"),
#             ).get(),
#             payload={}
#         )
#         res = await self.fetch(req)
#         return res if res is not None else []
#
#     async def get_erc20_txs(self, address: str, **kwargs) -> ResultQueue:
#         params = {
#             'module': 'account',
#             'action': 'tokentx',
#             'address': address,
#             'sort': 'asc',
#             'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
#             'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
#             'apikey': self.scan.get_key()
#         }
#
#         req = Request(
#             url=Url(domain=self.scan.domain, params=params).get(),
#             method="GET",
#             headers=Headers(
#                 accept=HEADER.get("accept"),
#                 content_type=HEADER.get("content-type"),
#                 user_agents=HEADER.get("user-agents"),
#             ).get(),
#             payload={}
#         )
#         res = await self.fetch(req)
#         return res if res is not None else []
#
#     async def get_erc721_txs(self, address: str, **kwargs) -> ResultQueue:
#         params = {
#             'module': 'account',
#             'action': 'tokennfttx',
#             'address': address,
#             'sort': 'asc',
#             'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
#             'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
#             'apikey': self.scan.get_key()
#         }
#
#         req = Request(
#             url=Url(domain=self.scan.domain, params=params).get(),
#             method="GET",
#             headers=Headers(
#                 accept=HEADER.get("accept"),
#                 content_type=HEADER.get("content-type"),
#                 user_agents=HEADER.get("user-agents"),
#             ).get(),
#             payload={}
#         )
#         res = await self.fetch(req)
#         return res if res is not None else []


# class ContractSpider(AccountSpider):
#     def __init__(self, vm: Vm, net: Net, module: Module):
#         super().__init__(vm, net, module)
#
#     async def get_abi(self, address: str):
#         params = {
#             'module': self.rpc.get(Mode.ABI.value).get("params").get("module"),
#             'action': self.rpc.get(Mode.ABI.value).get("params").get("action"),
#             'address': address,
#             'apikey': self.scan.get_key()
#         }
#         req = Request(
#             url=Url(domain=self.scan.domain, params=params).get(),
#             method="GET",
#             headers=Headers(
#                 accept=HEADER.get("accept"),
#                 content_type=HEADER.get("content-type"),
#                 user_agents=HEADER.get("user-agents"),
#             ).get(),
#             payload={}
#         )
#         res = await self.fetch(req)
#         return Result(
#             key=address,
#             item=ABI().map({'address': address, 'abi': res})
#             if res not in [
#                 None, 'Contract source code not verified',
#                 'Max rate limit reached'
#             ] else None
#         )


class ABISpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.AC, Mode.ABI)

    async def parse(self, **kwargs):
        key = kwargs.get('id')
        address = kwargs.get('key')

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
        return Result(
            key=key,
            item=ABI().map({'address': address, 'abi': res}).dict()
            if res not in [
                None, 'Contract source code not verified',
                'Max rate limit reached'
            ] else None
        )


class TxListSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net, Module.AC, Mode.TXLIST)
        self.start_blk = 0
        self.end_blk = 9_999_999_999

    async def parse(self, **kwargs):
        key = kwargs.get('id')
        address = kwargs.get('address')

        kwargs = {k: v for k, v in kwargs.items() if k not in ['id', 'address']}
        tasks = [
            asyncio.create_task(self.get_external_txs(address, **kwargs)),
            asyncio.create_task(self.get_internal_txs(address, **kwargs)),
            asyncio.create_task(self.get_erc20_txs(address, **kwargs)),
            asyncio.create_task(self.get_erc721_txs(address, **kwargs))
        ]
        ext_txs, int_txs, erc20_txs, erc721_txs = await asyncio.gather(*tasks)
        res = ext_txs + int_txs + erc20_txs + erc721_txs

        return Result(
            key=key,
            item=TxList().map({'array': res}).dict()
            if len(res) != 0 else {}
        )

    async def get_external_txs(self, address: str, **kwargs) -> list:
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'sort': 'asc',
            'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
            'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
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

        try:
            return [{**e, 'txType': 'external tx'} for e in res] if res not in [
                None, 'Contract source code not verified',
                'Max rate limit reached'
            ] else []
        except TypeError as e:
            logging.error(e)
            return []

    async def get_internal_txs(self, address: str, **kwargs) -> list:
        params = {
            'module': 'account',
            'action': 'txlistinternal',
            'address': address,
            'sort': 'asc',
            'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
            'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
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

        try:
            return [{**e, 'txType': 'internal tx'} for e in res] if res not in [
                None, 'Contract source code not verified',
                'Max rate limit reached'
            ] else []
        except TypeError as e:
            logging.error(e)
            return []

    async def get_erc20_txs(self, address: str, **kwargs) -> list:
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': address,
            'sort': 'asc',
            'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
            'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
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

        try:
            return [{**e, 'txType': 'erc20 tx'} for e in res] if res not in [
                None, 'Contract source code not verified',
                'Max rate limit reached'
            ] else []
        except TypeError as e:
            logging.error(e)
            return []

    async def get_erc721_txs(self, address: str, **kwargs) -> list:
        params = {
            'module': 'account',
            'action': 'tokennfttx',
            'address': address,
            'sort': 'asc',
            'startblock': max(kwargs.get('startblock', self.start_blk), self.start_blk),
            'endblock': min(kwargs.get('endblock', self.end_blk), self.end_blk),
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

        try:
            return [{**e, 'txType': 'erc721 tx'} for e in res] if res not in [
                None, 'Contract source code not verified',
                'Max rate limit reached'
            ] else []
        except TypeError as e:
            logging.error(e)
            return []


# spider = AccountSpider(Vm.EVM, Net.ETH, Module.AC)
# asyncio.get_event_loop().run_until_complete(spider.get(
#     mode=Mode.TXLIST,
#     key="0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",
#     startblock=int("0x109d8f5", 16),
#     endblock=int("0x109d8f5", 16),
# ))