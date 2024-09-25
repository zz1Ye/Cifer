import argparse

from spider.fty import Factory
from spider.meta import Param
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
                                 'ts', 'in', 'el', 'ffs'], type=str, default='trans')
    parser.add_argument('-hash', '--hashes', help="Transaction or Block Hash List (,)",
                        type=lambda x: [e.strip() for e in x.split(',')], default=[])
    parser.add_argument('-a', '--addresses', help="Contract Address List (,)",
                        type=lambda x: [e.strip() for e in x.split(',')], default=[])
    parser.add_argument('-o', '--output', help="Output Dir", type=str, default='out/')
    parser.add_argument('-bs', '--batchsize', help="Batch Size", type=int, default=16)

    args = parser.parse_args()

    vm, net, module, mode = Vm(args.vm), Net(args.net), Module(args.module), Mode(args.mode)
    hashes, addresses, out = args.hashes, args.addresses, args.output
    batch_size = args.batchsize

    meta = Factory().create_crawler(vm, net, module, mode, batch_size)

    if hashes:
        await meta.parse([Param(query={'hash': h}, out=out) for h in hashes])

    if addresses:
        await meta.parse([Param(query={'address': a}, out=out) for a in addresses])
