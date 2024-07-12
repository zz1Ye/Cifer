#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : tx.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from pydantic import BaseModel

from item.meta import Item


class Transaction(Item):
    def map(self, source: dict):
        self.hash = source.get('hash')
        self.block_hash = source.get('block_hash')
        self.block_number = source.get('block_number')
        self.from_address = source.get('from_address')
        self.to_address = source.get('to_address')
        self.value = source.get('value')
        self.timestamp = source.get('timestamp')
        self.gas = source.get('gas')
        self.gas_price = source.get('gas_price')
        self.input = source.get('input')
        self.nonce = source.get('nonce')
        self.type = source.get('type')
        self.chain_id = source.get('chain_id')

    hash: str
    block_hash: str
    block_number: int
    from_address: str
    to_address: str
    value: int
    timestamp: int
    gas: int
    gas_price: int
    input: str
    nonce: str
    type: str
    chain_id: int




class TraceAction(BaseModel):
    from_address: str
    to_address: str
    call_type: str
    gas: int
    input: str
    value: int


class Trace(BaseModel):
    action: TraceAction
    block_hash: str
    block_number: int
    result: dict
    subtraces: int
    trace_address: list
    transaction_hash: str
    transaction_position: int
    type: str


# Receipt
class Receipt(BaseModel):
    block_number: int
    block_hash: str
    contract_address: str
    from_address: str
    logs: list
    status: bool
    to_address: str


class Logs(BaseModel):
    address: str
    data: str
    topics: list
    block_number: int
    transaction_hash: str
    trainsaction_index: int
    block_hash: str
    log_index: int
    removed: bool

