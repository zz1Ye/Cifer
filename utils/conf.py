#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : conf.py
@Time   : 2024/7/10 9:25
@Author : zzYe

"""
from enum import Enum

from item.evm.blk import Block
from item.evm.ps import Timestamp, Subgraph, Input, EventLog, CompleteForm
from item.evm.sc import ABI
from item.evm.tx import Transaction, Trace, Receipt


class Vm(Enum):
    EVM = "evm"


class Net(Enum):
    ETH = "eth"
    BSC = "bsc"
    POL = "pol"


class Module(Enum):
    TX = "tx"
    BLK = "blk"
    SC = "sc"
    PS = 'ps'

    def allowed_modes(self):
        return {
            Module.TX: {Mode.TRANS, Mode.TRACE, Mode.RCPT},
            Module.BLK: {Mode.BLOCK},
            Module.SC: {Mode.ABI},
            Module.PS: {Mode.TS, Mode.SG, Mode.IN, Mode.EL, Mode.CF}
        }.get(self)


class Mode(Enum):
    TS = 'ts'
    SG = 'sg'
    IN = 'in'
    EL = 'el'
    CF = 'cf'
    TRANS = 'trans'
    TRACE = 'trace'
    RCPT = 'rcpt'
    BLOCK = 'block'
    ABI = 'abi'

    def new_mapping_item(self):
        return {
            Mode.TRANS: Transaction(),
            Mode.TRACE: Trace(),
            Mode.RCPT: Receipt(),
            Mode.BLOCK: Block(),
            Mode.ABI: ABI(),
            Mode.TS: Timestamp(),
            Mode.SG: Subgraph(),
            Mode.IN: Input(),
            Mode.EL: EventLog(),
            Mode.CF: CompleteForm()
        }.get(self)

    @staticmethod
    def is_allowed(mode, module):
        modes = Module(module).allowed_modes()
        return mode in modes





