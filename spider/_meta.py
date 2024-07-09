#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : _meta.py
@Time   : 2024/7/9 12:42
@Author : zzYe

"""
import aiohttp


class EVMSpider:
    def __init__(self, **kwargs):
        pass

    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            content = await response.read()
            return content
