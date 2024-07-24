#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : meta.py
@Time   : 2024/7/12 9:12
@Author : zzYe

"""
from functools import wraps

from pydantic import BaseModel

from utils.data import snake_keys_to_camel


def check_source(func):
    @wraps(func)
    def wrapper(self, source):
        if source is None or not isinstance(source, dict):
            source = {}
        return func(self, source)
    return wrapper


def snake_to_camel(func):
    @wraps(func)
    def wrapper(self, source):
        source = snake_keys_to_camel(source)
        return func(self, source)
    return wrapper


class Item(BaseModel):
    def id(self):
        return '{}-{}'.format(
            self.__class__.__qualname__,
            str(self.dict())
        )

    @snake_to_camel
    @check_source
    def map(self, source: dict):
        raise NotImplementedError()
