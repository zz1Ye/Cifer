#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : _meta.py
@Time   : 2024/7/9 12:42
@Author : zzYe

"""
import asyncio
from functools import partial

import aiohttp

from utils.req import get_headers


class EVMSpider:
    def __init__(self, **kwargs):
        pass

    @classmethod
    async def fetch(cls, url):
        async with aiohttp.ClientSession(headers=get_headers()) as session:
            async with session.get(url) as response:
                content = await response.text()
                print(content)
            return content


if __name__ == '__main__':
    spider = EVMSpider
    partial_coro = partial(spider.fetch, url="https://blog.csdn.net/python_dj/article/details/120059391")
    asyncio.run(partial_coro())
