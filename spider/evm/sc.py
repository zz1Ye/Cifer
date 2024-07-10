#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sc.py
@Time   : 2024/7/9 16:40
@Author : zzYe

"""
from spider._meta import Spider
from utils.conf import Net
from utils.req import join_url, Method


class ContractSpider(Spider):
    def __init__(self, net: Net):
        super().__init__(net)
        self.domain = self.api

    async def get_abi(self, address: str):
        params = {
            'module': 'contract',
            'action': 'getabi',
            'address': address,
            'apikey': self.api_keys[0]
        }
        url = join_url(params)

        return await self.fetch(url, Method.GET.value)
