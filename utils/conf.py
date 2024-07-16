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
    TRANS = "tx.transaction"
    TRACE = "tx.trace"
    RCPT = "tx.receipt"
    BLOCK = "blk.block"
    ABI = "sc.abi"

    TS = "ps.timestamp"
    SG = "ps.subgraph"
    IN = "ps.input"
    EL = "ps.eventlog"

    TX = "tx"
    BLK = "blk"
    SC = "sc"


