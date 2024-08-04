import argparse

from tqdm import tqdm

from spider.evm.blk import BlockSpider
from spider.evm.ps import TimestampParser, SubgraphParser, InputParser, EventLogParser, CompleteFormParser
from spider.evm.ac import ContractSpider
from spider.evm.tx import TransactionSpider
from spider.meta import Spider
from utils.conf import Vm, Net, Module, Mode


async def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vm', help="Select Virtual Machine.",
                        choices=['evm'], type=str, default='evm')
    parser.add_argument('-n', '--net', help="Select Network.",
                        choices=['eth', 'bsc', 'pol'], type=str, default='eth')
    parser.add_argument('-m', '--module', help="Select Module.",
                        choices=['tx', 'blk', 'sc', 'ps'], type=str, default='tx')
    parser.add_argument('-mode', '--mode', help="Select mode.",
                        choices=['trans', 'trace', 'rcpt', 'abi', 'block',
                                 'ts', 'sg', 'in', 'el', 'cf'], type=str, default='trans')
    parser.add_argument('-hash', '--hashes', help="Transaction or Block Hash List (,)",
                        type=lambda x: [e.strip() for e in x.split(',')], default=[])
    parser.add_argument('-a', '--addresses', help="Contract Address List (,)",
                        type=lambda x: [e.strip() for e in x.split(',')], default=[])
    parser.add_argument('-o', '--output', help="Output Dir", type=str, default='out/')
    parser.add_argument('-bs', '--batchsize', help="Batch Size", type=int, default=1024)

    args = parser.parse_args()

    vm, net, module, mode = Vm(args.vm), Net(args.net), Module(args.module), Mode(args.mode)
    hashes, addresses, out = args.hashes, args.addresses, args.output
    batch_size = args.batchsize

    meta = {
        Mode.TRANS: TransactionSpider(vm, net, module),
        Mode.TRACE: TransactionSpider(vm, net, module),
        Mode.RCPT: TransactionSpider(vm, net, module),
        Mode.BLOCK: BlockSpider(vm, net, module),
        Mode.ABI: ContractSpider(vm, net, module),
        Mode.TS: TimestampParser(vm, net, module),
        Mode.SG: SubgraphParser(vm, net, module),
        Mode.IN: InputParser(vm, net, module),
        Mode.EL: EventLogParser(vm, net, module),
        Mode.CF: CompleteFormParser(vm, net, module),
    }[mode]

    keys = hashes if hashes else addresses

    for i in tqdm(range(0, len(keys), batch_size)):
        if issubclass(type(meta), Spider):
            await meta.crawl(keys=keys[i:i+batch_size], mode=mode, out=out)
        else:
            await meta.parse(keys=keys[i:i + batch_size], mode=mode, out=out)
