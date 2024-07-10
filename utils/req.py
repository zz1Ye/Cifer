#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : req.py
@Time   : 2024/7/9 15:57
@Author : zzYe

"""
import random
from enum import Enum

from pydantic import BaseModel

from settings import HEADERS_LIST
from urllib.parse import urlencode, urljoin


class Method(Enum):
    GET = "GET"
    POST = "POST"


class Url(BaseModel):
    domain: str
    params: dict

    def get(self):
        domain = self.domain if self.domain.endswith('/') else self.domain + '/'
        query = urlencode(self.params)

        return urljoin(
            domain, '?' + query
        )


class Headers(BaseModel):
    accept: str
    content_type: str
    user_agent: str

    def get(self):
        return {
            k.replace('_', '-'): v
            for k, v in self.dict().items()
        }


class Request(BaseModel):
    url: Url
    method: Method
    headers: dict
    payload: dict


def get_user_agent():
    return {'User-Agent': random.choice(HEADERS_LIST)}

