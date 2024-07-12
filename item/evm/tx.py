#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   : tx.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from typing import List
from item.meta import Item


class Transaction(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/eth_getTransactionByHash
    """
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        self.hash = source.get('hash')
        self.transaction_index = source.get('transactionIndex')
        self.block_hash = source.get('blockHash')
        self.block_number = source.get('blockNumber')
        self.from_address = source.get('from')
        self.to_address = source.get('to')
        self.gas = source.get('gas')
        self.gas_price = source.get('gasPrice')
        self.max_fee_per_gas = source.get('maxFeePerGas')
        self.max_priority_fee_per_gas = source.get('maxPriorityFeePerGas')
        self.value = source.get('value')
        self.input = source.get('input')
        self.nonce = source.get('nonce')
        self.type = source.get('type')
        self.access_list = source.get('accesslist')
        self.chain_id = source.get('chainId')
        self.v = source.get('v')
        self.r = source.get('r')
        self.s = source.get('s')

    hash: str
    transaction_index: str
    block_hash: str
    block_number: str
    from_address: str
    to_address: str
    gas: str
    gas_price: str
    max_fee_per_gas: str
    max_priority_fee_per_gas: str
    value: str
    input: str
    nonce: str
    type: str
    access_list: list
    chain_id: str
    v: str
    r: str
    s: str


class TraceAction(Item):
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        self.from_address = source.get('from')
        self.to_address = source.get('to')
        self.call_type = source.get('callType')
        self.gas = source.get('gas')
        self.input = source.get('input')
        self.value = source.get('value')
        self.author = source.get('author')
        self.reward_type = source.get('rewardType')

    from_address: str
    to_address: str
    call_type: str
    gas: str
    input: str
    value: str
    author: str
    reward_type: str


class TraceResult(Item):
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        self.gas_used = source.get('gasUsed')
        self.output = source.get('output')

    gas_used: str
    output: str


class TraceElement(Item):
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        action = TraceAction()
        result = TraceResult()
        action.map(source.get('action'))
        result.map(source.get('result'))

        self.action = action
        self.block_hash = source.get('blockHash')
        self.block_number = source.get('blockNumber')
        self.result = result
        self.subtraces = source.get('subtraces')
        self.trace_address = source.get('traceAddress')
        self.transaction_hash = source.get('transactionHash')
        self.type = source.get('type')

    action: TraceAction
    block_hash: str
    block_number: str
    result: TraceResult
    subtraces: str
    trace_address: list
    transaction_hash: str
    type: str


class Trace(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/trace_transaction
    """
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        array = []
        for e in source.get('array'):
            element = TraceElement()
            element.map(e)
            array.append(element)
        self.array = array

    array: List[TraceElement]


class ReceiptLog(Item):
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        self.address = source.get('address')
        self.data = source.get('data')
        self.topics = source.get('topics')
        self.block_number = source.get('blockNumber')
        self.transaction_hash = source.get('transactionHash')
        self.trainsaction_index = source.get('trainsactionIndex')
        self.block_hash = source.get('blockHash')
        self.log_index = source.get('logIndex')
        self.removed = source.get('removed')

    address: str
    data: str
    topics: list
    block_number: int
    transaction_hash: str
    trainsaction_index: int
    block_hash: str
    log_index: int
    removed: bool


class Receipt(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/eth_getTransactionReceipt

    """
    def __init__(self, **data):
        super().__init__(**data)
        self._values_set = False

    def map(self, source: dict):
        logs = []
        for e in source.get('logs'):
            log = ReceiptLog()
            log.map(e)
            logs.append(log)
        self.block_number = source.get('blockNumber')
        self.block_hash = source.get('blockHash')
        self.contract_address = source.get('contractAddress')
        self.effective_gas_price = source.get('effectiveGasPrice')
        self.from_address = source.get('from')
        self.logs = logs
        self.logs_bloom = source.get('logsBloom')
        self.status = source.get('status')
        self.to_address = source.get('to')
        self.transaction_hash = source.get('transactionHash')
        self.transaction_index = source.get('transactionIndex')
        self.type = source.get('type')

    block_number: str
    block_hash: str
    contract_address: str
    effective_gas_price: str
    from_address: str
    logs: List[ReceiptLog]
    logs_bloom: str
    status: bool
    to_address: str
    transaction_hash: str
    transaction_index: str
    type: str


