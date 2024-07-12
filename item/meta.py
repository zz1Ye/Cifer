#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : meta.py
@Time   : 2024/7/12 9:12
@Author : zzYe

"""
from pydantic import BaseModel


class Item(BaseModel):
    def map(self, source: dict):
        raise NotImplementedError()
