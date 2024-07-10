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
