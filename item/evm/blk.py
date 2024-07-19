#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : blk.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from pydantic import Field

from item.meta import Item, check_source, snake_to_camel


class Block(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/eth_getBlockByHash
    """
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.number = source.get('number')
        self.hash = source.get('hash')
        self.parent_hash = source.get('parentHash')
        self.nonce = source.get('nonce')
        self.difficulty = source.get('difficulty')
        self.total_difficulty = source.get('totalDifficulty')
        self.logs_bloom = source.get('logsBloom')
        self.sha3uncles = source.get('sha3uncles')
        self.extra_data = source.get('extraData')
        self.timestamp = source.get('timestamp')
        self.size = source.get('size')
        self.miner = source.get('miner')
        self.transactions_root = source.get('transactionsRoot')
        self.state_root = source.get('stateRoot')
        self.receipts_root = source.get('receiptsRoot')
        self.uncles = source.get('uncles')
        self.transactions = source.get('transactions')
        self.gas_used = source.get('gasUsed')
        self.gas_limit = source.get('gasLimit')
        self.mix_hash = source.get('mixHash')
        self.base_fee_per_gas = source.get('baseFeePerGas')
        return self

    number: str = Field(default='')
    hash: str = Field(default='')
    parent_hash: str = Field(default='')
    nonce: str = Field(default='')
    difficulty: str = Field(default='')
    total_difficulty: str = Field(default='')
    logs_bloom: str = Field(default='')
    sha3uncles: str = Field(default='')
    extra_data: str = Field(default='')
    timestamp: str = Field(default='')
    size: str = Field(default='')
    miner: str = Field(default='')
    transactions_root: str = Field(default='')
    state_root: str = Field(default='')
    receipts_root: str = Field(default='')
    uncles: list = Field(default=[])
    transactions: list = Field(default=[])
    gas_used: str = Field(default='')
    gas_limit: str = Field(default='')
    mix_hash: str = Field(default='')
    base_fee_per_gas: str = Field(default='')
