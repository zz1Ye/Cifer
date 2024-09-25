import asyncio
import logging
from typing import List

from item.evm.ac import ABI, TxList
from settings import HEADER
from spider._meta import Spider, Param
from utils.conf import Net, Vm, Module, Mode
from utils.req import Request, Headers, Url, Result


class ABISpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.AC, Mode.ABI
        self.rpc = self.rpc.get(self.module.value, {}).get(self.mode.value, {})

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for p in params:
            key, address = p.id, p.query.get('address')
            query = {
                'module': self.rpc.get("params").get("module"),
                'action': self.rpc.get("params").get("action"),
                'address': address,
                'apikey': self.scan.get_key()
            }
            req = Request(
                url=Url(domain=self.scan.domain, params=query).get(),
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
                    ] else {}
                )
            )
        return res_arr


class TxListSpider(Spider):
    def __init__(self, vm: Vm, net: Net):
        super().__init__(vm, net)
        self.module, self.mode = Module.AC, Mode.TXLIST
        self.rpc = self.rpc.get(self.module.value, {}).get(self.mode.value, {})
        self.start_blk = 0
        self.end_blk = 9_999_999_999

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for p in params:
            key, address = p.id, p.query.get('address')
            kwargs = {k: v for k, v in p.query.items() if k not in ['address']}
            tasks = [
                asyncio.create_task(self.get_external_txs(address, **kwargs)),
                asyncio.create_task(self.get_internal_txs(address, **kwargs)),
                asyncio.create_task(self.get_erc20_txs(address, **kwargs)),
                asyncio.create_task(self.get_erc721_txs(address, **kwargs))
            ]
            ext_txs, int_txs, erc20_txs, erc721_txs = await asyncio.gather(*tasks)
            res = ext_txs + int_txs + erc20_txs + erc721_txs

            res_arr.append(
                Result(
                    key=key,
                    item=TxList().map({'array': res}).dict()
                    if len(res) != 0 else {}
                )
            )
        return res_arr

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
            logging.error(e, exc_info=True)
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
            logging.error(e, exc_info=True)
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
            logging.error(e, exc_info=True)
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
            logging.error(e, exc_info=True)
            return []
