#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File   : ts.py
@Time   : 2024/7/9 16:42
@Author : zzYe

"""
from typing import List

from pydantic import Field

from item.meta import Item, check_source


class Transaction(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/eth_getTransactionByHash
    """
    @check_source
    def map(self, source: dict):
        self.hash = source.get('hash')
        self.transaction_index = source.get('transactionIndex')
        self.block_hash = source.get('blockHash')
        self.block_number = source.get('blockNumber')
        self.from_ = source.get('from')
        self.to_ = source.get('to')
        self.gas = source.get('gas')
        self.gas_price = source.get('gasPrice')
        self.max_fee_per_gas = source.get('maxFeePerGas')
        self.max_priority_fee_per_gas = source.get('maxPriorityFeePerGas')
        self.value = source.get('value')
        self.input = source.get('input')
        self.nonce = source.get('nonce')
        self.type = source.get('type')
        self.accesslist = source.get('accesslist')
        self.chain_id = source.get('chainId')
        self.v = source.get('v')
        self.r = source.get('r')
        self.s = source.get('s')

    hash: str = Field(default='')
    transaction_index: str = Field(default='')
    block_hash: str = Field(default='')
    block_number: str = Field(default='')
    from_: str = Field(default='')
    to_: str = Field(default='')
    gas: str = Field(default='')
    gas_price: str = Field(default='')
    max_fee_per_gas: str = Field(default='')
    max_priority_fee_per_gas: str = Field(default='')
    value: str = Field(default='')
    input: str = Field(default='')
    nonce: str = Field(default='')
    type: str = Field(default='')
    accesslist: list = Field(default=[])
    chain_id: str = Field(default='')
    v: str = Field(default='')
    r: str = Field(default='')
    s: str = Field(default='')


class TraceAction(Item):
    @check_source
    def map(self, source: dict):
        self.from_ = source.get('from')
        self.to_ = source.get('to')
        self.call_type = source.get('callType')
        self.gas = source.get('gas')
        self.input = source.get('input')
        self.value = source.get('value')
        self.author = source.get('author')
        self.reward_type = source.get('rewardType')

    from_: str = Field(default='')
    to_: str = Field(default='')
    call_type: str = Field(default='')
    gas: str = Field(default='')
    input: str = Field(default='')
    value: str = Field(default='')
    author: str = Field(default='')
    reward_type: str = Field(default='')


class TraceResult(Item):
    @check_source
    def map(self, source: dict):
        self.gas_used = source.get('gasUsed')
        self.output = source.get('output')

    gas_used: str = Field(default='')
    output: str = Field(default='')


class TraceElement(Item):
    @check_source
    def map(self, source: dict):
        action = TraceAction()
        result = TraceResult()
        action.map(source.get('action') if 'action' in source else None)
        result.map(source.get('result') if 'result' in source else None)

        self.action = action
        self.block_hash = source.get('blockHash')
        self.block_number = source.get('blockNumber')
        self.result = result
        self.subtraces = source.get('subtraces')
        self.trace_address = source.get('traceAddress')
        self.transaction_hash = source.get('transactionHash')
        self.transaction_position = source.get('transactionPosition')
        self.type = source.get('type')

    action: TraceAction = Field(default=None)
    block_hash: str = Field(default='')
    block_number: int = Field(default=0)
    result: TraceResult = Field(default=None)
    subtraces: int = Field(default=0)
    trace_address: list = Field(default=[])
    transaction_hash: str = Field(default='')
    transaction_position: int = Field(default=0)
    type: str = Field(default='')


class Trace(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/trace_transaction
    """
    @check_source
    def map(self, source: dict):
        array = []
        for e in source.get('array'):
            element = TraceElement()
            element.map(e)
            array.append(element)
        self.array = array

    array: List[TraceElement] = Field(default=[])


class ReceiptLog(Item):
    @check_source
    def map(self, source: dict):
        self.address = source.get('address')
        self.data = source.get('data')
        self.topics = source.get('topics')
        self.block_number = source.get('blockNumber')
        self.transaction_hash = source.get('transactionHash')
        self.trainsaction_index = source.get('transactionIndex')
        self.block_hash = source.get('blockHash')
        self.log_index = source.get('logIndex')
        self.removed = source.get('removed')

    address: str = Field(default='')
    data: str = Field(default='')
    topics: list = Field(default=[])
    block_number: str = Field(default='')
    transaction_hash: str = Field(default='')
    trainsaction_index: str = Field(default='')
    block_hash: str = Field(default='')
    log_index: str = Field(default='')
    removed: bool = Field(default=False)


class Receipt(Item):
    """
    Url:
        https://www.chainnodes.org/docs/ethereum/eth_getTransactionReceipt

    """
    @check_source
    def map(self, source: dict):
        logs = []
        for e in source.get('logs', []):
            log = ReceiptLog()
            log.map(e)
            logs.append(log)
        self.block_number = source.get('blockNumber')
        self.block_hash = source.get('blockHash')
        self.contract_address = source.get('contractAddress')
        self.effective_gas_price = source.get('effectiveGasPrice')
        self.from_ = source.get('from')
        self.logs = logs
        self.logs_bloom = source.get('logsBloom')
        self.status = source.get('status')
        self.to_ = source.get('to')
        self.transaction_hash = source.get('transactionHash')
        self.transaction_index = source.get('transactionIndex')
        self.type = source.get('type')

    block_number: str = Field(default='')
    block_hash: str = Field(default='')
    contract_address: str = Field(default='')
    effective_gas_price: str = Field(default='')
    from_: str = Field(default='')
    logs: List[ReceiptLog] = Field(default=[])
    logs_bloom: str = Field(default='')
    status: str = Field(default='')
    to_: str = Field(default='')
    transaction_hash: str = Field(default='')
    transaction_index: str = Field(default='')
    type: str = Field(default='')


