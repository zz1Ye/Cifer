#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : conf.py
@Time   : 2024/7/10 9:25
@Author : zzYe

"""
from enum import Enum


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
            Module.PS: {Mode.TS, Mode.SG, Mode.IN, Mode.EL}
        }.get(self)


class Mode(Enum):
    TS = 'ts'
    SG = 'sg'
    IN = 'in'
    EL = 'el'
    TRANS = 'trans'
    TRACE = 'trace'
    RCPT = 'rcpt'
    BLOCK = 'block'
    ABI = 'abi'

    @staticmethod
    def is_allowed(mode, module):
        modes = Module(module).allowed_modes()
        return mode in modes





