#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : meta.py
@Time   : 2024/7/12 9:12
@Author : zzYe

"""
from functools import wraps

from pydantic import BaseModel


def check_source(func):
    @wraps(func)
    def wrapper(self, source):
        if source is None or not isinstance(source, dict):
            return None
        return func(self, source)
    return wrapper


class Item(BaseModel):
    def id(self):
        return '{}_{}'.format(
            self.__class__.__qualname__,
            str(self.dict())
        )

    def map(self, source: dict):
        raise NotImplementedError()
