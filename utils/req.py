#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : req.py
@Time   : 2024/7/9 15:57
@Author : zzYe

"""
import random
from enum import Enum

from settings import HEADERS_LIST
from urllib.parse import urlencode, urljoin


class Method(Enum):
    GET = "GET"
    POST = "POST"


def get_headers():
    return {'User-Agent': random.choice(HEADERS_LIST)}


def join_url(domain: str, params: dict):
    domain = domain if domain.endswith('/') else domain + '/'
    query = urlencode(params)

    url = urljoin(
        domain, '?' + query
    )

    return url
