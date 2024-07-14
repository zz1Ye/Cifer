#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sc.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from pydantic import Field

from item.meta import Item


class ABI(Item):
    """
    Url
        https://docs.ethersscan.io/api-endpoints/contracts
    """
    def map(self, source: dict):
        if source is None or not isinstance(source, dict):
            return

        self.address = source.get('address')
        self.abi = source.get('abi')

    address: str = Field(default='')
    abi: str = Field(default='')


