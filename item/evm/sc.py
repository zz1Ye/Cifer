#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sc.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from item.meta import Item


class ABI(Item):
    """
    Url
        https://docs.ethersscan.io/api-endpoints/contracts
    """
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        self.address = source.get('address')
        self.abi = source.get('abi')

    address: str
    abi: str


