#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ts.py
@Time   : 2024/7/11 16:19
@Author : zzYe

"""
from item.evm.blk import Block
from item.evm.tx import Transaction


class TransactionParser:
    def __init__(self):
        pass

    def parse(self, trans: Transaction, block: Block):
        tx = trans.dict()
        tx["timestamp"] = block.timestamp
        return tx

    # async def parse(self, hash: str):
    #     tx =