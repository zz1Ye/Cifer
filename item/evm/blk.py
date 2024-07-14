#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : blk.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from pydantic import Field

from item.meta import Item


class Block(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/eth_getBlockByHash
    """
    def map(self, source: dict):
        if source is None or not isinstance(source, dict):
            return

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

    number: int = Field(default=0)
    hash: str = Field(default='')
    parent_hash: str = Field(default='')
    nonce: str = Field(default='')
    difficulty: int = Field(default=0)
    total_difficulty: str = Field(default='')
    logs_bloom: str = Field(default='')
    sha3uncles: str = Field(default='')
    extra_data: str = Field(default='')
    timestamp: int = Field(default=0)
    size: str = Field(default='')
    transactions_root: str = Field(default='')
    state_root: str = Field(default='')
    receipts_root: str = Field(default='')
    uncles: list = Field(default=[])
    transactions: list = Field(default=[])
    mix_hash: str = Field(default='')

