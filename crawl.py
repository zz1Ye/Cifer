#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : crawl.py
@Time   : 2024/7/11 16:31
@Author : zzYe

"""
import asyncio
import csv
import os
from queue import Queue

from tqdm import tqdm

from dao.meta import JsonDao
from item.evm.blk import Block
from item.evm.tx import Transaction, Trace, Receipt
from spider.evm.blk import BlockSpider
from spider.evm.tx import TransactionSpider
from utils.conf import Vm, Net, Module
from utils.pc import Task, Job, PC


# async def main():
#     csv_fpath = "out/label.csv"
#     vm = Vm.EVM
#
#     todo = []
#     output_dir = f'../out/{vm.value}'
#
#     todo = []
#     jobs = Queue()
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/tx"
#         with os.scandir(cur_dir) as entries:
#             for h in [entry.name for entry in entries if entry.is_dir()]:
#
#                 ms = []
#                 if not os.path.exists(f"{cur_dir}/{h}/trans.json"):
#                     ms.append('trans')
#
#                 if not os.path.exists(f"{cur_dir}/{h}/trace.json"):
#                     ms.append('trace')
#
#                 if not os.path.exists(f"{cur_dir}/{h}/rcpt.json"):
#                     ms.append('rcpt')
#
#                 module = Module.TX
#
#                 if len(ms) != 0:
#                     job = Job([
#                         Task(
#                             spider=TransactionSpider(
#                                 vm=vm,
#                                 net=net,
#                                 module=module
#                             ),
#                             params={'mode': m, 'hash': h},
#                             item={'trans': Transaction(), 'trace': Trace(), 'rcpt': Receipt()}[m],
#                             dao=JsonDao(fpath=f"{output_dir}/{net.value}/{module.value}/{h}/{m}.json")
#                         )
#                         for m in ms
#                     ])
#                     jobs.put(job)
#
#     pc = PC(jobs)
#     await pc.run()
#
#
# asyncio.get_event_loop().run_until_complete(main())


async def main():
    csv_fpath = "out/label.csv"
    vm = Vm.EVM

    todo = []
    output_dir = f'../out/{vm.value}'

    todo = []
    for net in [Net.ETH, Net.BSC, Net.POL]:
        cur_dir = f"{output_dir}/{net.value}/tx"
        with os.scandir(cur_dir) as entries:
            for h in [entry.name for entry in entries if entry.is_dir()]:
                dao = JsonDao(fpath=f"{cur_dir}/{h}/trans.json")
                for tx in dao.load(batch_size=1):
                    if len(tx) > 0:
                        todo.append({
                            'net': net.value,
                            'block_hash': tx[0].get('block_hash', '').lower()
                        })

    jobs = Queue()
    # trans + trace + rcpt
    for e in tqdm(todo):
        hash = e.get('block_hash').lower()

        if e.get('net') == 'eth':
            net = Net.ETH
        elif e.get('net') == 'bsc':
            net = Net.BSC
        elif e.get('net') == 'pol':
            net = Net.POL
        else:
            continue

        module = Module.BLK
        job = Job([
            Task(
                spider=BlockSpider(
                    vm=vm,
                    net=net,
                    module=module
                ),
                params={'mode': m, 'hash': hash},
                item={'block': Block()}[m],
                dao=JsonDao(fpath=f"{output_dir}/{net.value}/{module.value}/{hash}/{m}.json")
            )
            for m in ['block']
        ])
        jobs.put(job)

    pc = PC(jobs)
    await pc.run()
asyncio.get_event_loop().run_until_complete(main())

# async def main():
#     csv_fpath = "out/label.csv"
#     vm = Vm.EVM
#
#     todo = []
#     output_dir = f'../out/{vm.value}'
#
#     # done = os.listdir(f"{output_dir}/eth/tx")
#     with open(csv_fpath, mode='r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             src, dst = row.get("Src"), row.get("Dst")
#             src_tx_hash = row.get("SrcTxHash")
#             dst_tx_hash = row.get("DstTxHash")
#
#             todo.append({
#                 'vm': vm.value, 'net': src.lower(),
#                 'hash': src_tx_hash.lower()
#             })
#             if dst != '':
#                 todo.append({
#                     'vm': vm.value, 'net': dst.lower(),
#                     'hash': dst_tx_hash.lower()
#                 })
#
#     jobs = Queue()
#     # trans + trace + rcpt
#     for e in tqdm(todo):
#         hash = e.get('hash').lower()
#
#         if e.get('net') == 'eth':
#             net = Net.ETH
#         elif e.get('net') == 'bsc':
#             net = Net.BSC
#         elif e.get('net') == 'pol':
#             net = Net.POL
#         else:
#             continue
#
#         job = Job([
#             Task(
#                 spider=TransactionSpider(
#                     vm=vm,
#                     net=net,
#                     module=Module.TX
#                 ),
#                 params={'mode': m, 'hash': hash},
#                 item={'trans': Transaction(), 'trace': Trace(), 'rcpt': Receipt()}[m],
#                 dao=JsonDao(fpath=f"{output_dir}/{net.value}/{Module.TX.value}/{hash}/{m}.json")
#             )
#             for m in ['trans', 'trace', 'rcpt']
#         ])
#         jobs.put(job)
#
#     pc = PC(jobs)
#     await pc.run()


# asyncio.get_event_loop().run_until_complete(main())




