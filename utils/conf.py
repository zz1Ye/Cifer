from enum import Enum

from item.evm.ac import ABI, TxList
from item.evm.blk import Block
from item.evm.ps import Timestamp, Input, EventLog, FundsFlowSubgraph
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
    AC = "ac"
    PS = 'ps'

    def allowed_modes(self):
        return {
            Module.TX: {Mode.TRANS, Mode.TRACE, Mode.RCPT},
            Module.BLK: {Mode.BLOCK},
            Module.AC: {Mode.ABI, Mode.TXLIST},
            Module.PS: {Mode.TS, Mode.IN, Mode.EL, Mode.FFS}
        }.get(self)


class Mode(Enum):
    TS = 'ts'
    IN = 'in'
    EL = 'el'
    TRANS = 'trans'
    TRACE = 'trace'
    RCPT = 'rcpt'
    BLOCK = 'block'
    ABI = 'abi'
    TXLIST = 'txlist'
    FFS = 'ffs'

    def new_mapping_item(self):
        return {
            Mode.TRANS: Transaction(),
            Mode.TRACE: Trace(),
            Mode.RCPT: Receipt(),
            Mode.BLOCK: Block(),
            Mode.ABI: ABI(),
            Mode.TXLIST: TxList(),
            Mode.TS: Timestamp(),
            Mode.IN: Input(),
            Mode.EL: EventLog(),
            Mode.FFS: FundsFlowSubgraph()
        }.get(self)

    @staticmethod
    def is_allowed(mode, module):
        modes = Module(module).allowed_modes()
        return mode in modes





