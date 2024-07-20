#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : crawl.py
@Time   : 2024/7/11 16:31
@Author : zzYe

"""
import asyncio
import csv
from queue import Queue
from typing import List

from tqdm import tqdm

from dao.meta import JsonDao
from item.evm.tx import Trace
from spider.evm.ps import SubgraphParser, InputParser, EventLogParser, TimestampParser, CompleteFormParser
from spider.evm.tx import TransactionSpider
from spider.meta import Parser
from utils.conf import Vm, Net, Module, Mode
from utils.pc import PC, Job


async def main():
    label_fpath = f'out/label.csv'
    tasks = {'eth': [], 'bsc': [], 'pol': []}
    with open(label_fpath, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            src, dst = row.get("Src"), row.get("Dst")
            src_tx_hash = row.get("SrcTxHash")
            dst_tx_hash = row.get("DstTxHash")

            tasks[src.lower()].append(src_tx_hash.lower())
            if dst != "" and dst_tx_hash != "":
                tasks[dst.lower()].append(dst_tx_hash.lower())

    batch_size = 64
    for k, v in tasks.items():
        vm = Vm.EVM
        if k == 'eth':
            net = Net.ETH
        elif k == 'bsc':
            net = Net.BSC
        elif k == 'pol':
            net = Net.POL
        module = Module.PS

        out = f"../out"
        parser = CompleteFormParser(vm, net, module)

        for i in tqdm(range(0, len(v), batch_size)):
            await parser.parse(keys=v[i:i+batch_size], mode=Mode.CF, out=out)


asyncio.get_event_loop().run_until_complete(main())



