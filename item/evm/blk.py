#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : blk.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from pydantic import BaseModel


class Block(BaseModel):
    number: int
    hash: str
    parent_hash: str
    nonce: str
    difficulty: int
    timestamp: int
    transactions: list
