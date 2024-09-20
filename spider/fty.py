from spider._meta import Crawlable
from spider.dec import AsyncSpider, CacheSpider
from spider.evm_.ac import ABISpider
from spider.evm_.blk import BlockSpider
from spider.evm_.ps import InputParser
from spider.evm_.tx import TransactionSpider, TraceSpider, ReceiptSpider
from utils.conf import Vm, Net, Module, Mode


class Factory:
    @staticmethod
    def create_crawler(vm: Vm, net: Net, module: Module, mode: Mode) -> Crawlable:
        crawler = {
            Module.TX: {
               Mode.TRANS: TransactionSpider(vm, net),
               Mode.TRACE: TraceSpider(vm, net),
               Mode.RCPT: ReceiptSpider(vm, net),
            },
            Module.AC: {
                Mode.ABI: ABISpider(vm, net),
            },
            Module.BLK: {
                Mode.BLOCK: BlockSpider(vm, net),
            },
            Module.PS: {
                Mode.IN: InputParser(vm, net)
            }

        }[module][mode]
        return CacheSpider(AsyncSpider(spider=crawler))
