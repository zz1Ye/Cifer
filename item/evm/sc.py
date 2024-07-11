#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sc.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from pydantic import BaseModel


class Contract(BaseModel):
    address: str
    abi: str


