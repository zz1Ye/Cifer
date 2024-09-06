from spider.evm.ps import FundsFlowSubgraphSpider, TimestampParser, InputParser
from spider.meta import Spider
from spider.evm.tx import TransactionSpider
from utils.conf import Vm, Net, Module, Mode


class Factory:
    @staticmethod
    def create_spider(vm: Vm, net: Net, module: Module, mode: Mode) -> Spider:
        return {
            Mode.TRANS: TransactionSpider(vm, net),
            Mode.TRACE: TransactionSpider(vm, net),
            Mode.RCPT: TransactionSpider(vm, net),
            Mode.FFS: FundsFlowSubgraphSpider(vm, net),
            # Mode.BLOCK: BlockSpider(vm, net, module),
            # Mode.ABI: ContractSpider(vm, net, module),
            Mode.TS: TimestampParser(vm, net),
            # Mode.SG: SubgraphParser(vm, net, module),
            Mode.IN: InputParser(vm, net),
            # Mode.EL: EventLogParser(vm, net, module),
            # Mode.CF: CompleteFormParser(vm, net, module),
        }[mode]
