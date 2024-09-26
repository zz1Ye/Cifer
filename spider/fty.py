from spider.meta import Crawlable
from spider.dec import AsyncSpider, CacheSpider
from spider.evm.ac import ABISpider, TxListSpider
from spider.evm.blk import BlockSpider
from spider.evm.ps import InputParser, EventLogParser, TimestampParser, FundsFlowSubgraphSpider
from spider.evm.tx import TransactionSpider, TraceSpider, ReceiptSpider
from utils.conf import Vm, Net, Module, Mode


class Factory:
    @staticmethod
    def create_crawler(vm: Vm, net: Net, module: Module, mode: Mode, batch_size: int = 16) -> Crawlable:
        crawler = {
            Module.TX: {
               Mode.TRANS: TransactionSpider(vm, net),
               Mode.TRACE: TraceSpider(vm, net),
               Mode.RCPT: ReceiptSpider(vm, net),
            },
            Module.AC: {
                Mode.ABI: ABISpider(vm, net),
                Mode.TXLIST: TxListSpider(vm, net)
            },
            Module.BLK: {
                Mode.BLOCK: BlockSpider(vm, net),
            },
            Module.PS: {
                Mode.TS: TimestampParser(vm, net),
                Mode.IN: InputParser(vm, net),
                Mode.EL: EventLogParser(vm, net),
                Mode.FFS: FundsFlowSubgraphSpider(vm, net),
            }

        }[module][mode]
        return CacheSpider(AsyncSpider(spider=crawler, batch_jobs=batch_size), batch_size=batch_size)
