#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : blk.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from item.meta import Item


class Block(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/eth_getBlockByHash
    """
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        self.number = source.get('number')
        self.hash = source.get('hash')
        self.parent_hash = source.get('parentHash')
        self.nonce = source.get('nonce')
        self.difficulty = source.get('difficulty')
        self.total_difficulty = source.get('totalDifficulty')
        self.logs_bloom = source.get('logs_bloom')
        self.sha3uncles = source.get('sha3uncles')
        self.extra_data = source.get('extraData')
        self.timestamp = source.get('timestamp')
        self.size = source.get('size')
        self.transactions_root = source.get('transactionsRoot')
        self.state_root = source.get('stateRoot')
        self.receipts_root = source.get('receiptsRoot')
        self.uncles = source.get('uncles')
        self.transactions = source.get('transactions')
        self.mix_hash = source.get('mixHash')

    number: int
    hash: str
    parent_hash: str
    nonce: str
    difficulty: int
    total_difficulty: str
    logs_bloom: str
    sha3uncles: str
    extra_data: str
    timestamp: int
    size: str
    transactions_root: str
    state_root: str
    receipts_root: str
    uncles: list
    transactions: list
    mix_hash: str

