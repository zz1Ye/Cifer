#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : crawl.py
@Time   : 2024/7/11 16:31
@Author : zzYe

"""
import asyncio
from queue import Queue

from dao.meta import JsonDao
from item.evm.tx import Trace
from spider.evm.ps import SubgraphParser, InputParser, EventLogParser
from spider.evm.tx import TransactionSpider
from utils.conf import Vm, Net, Module
from utils.pc import PC, Job


async def main():
    vm = Vm.EVM
    net = Net.ETH
    module = Module.TX

    out = f"out/{vm.value}/{net.value}"
    parser = EventLogParser(vm, net, module)
    hash = '0x2f13d202c301c8c1787469310a2671c8b57837eb7a8a768df857cbc7b3ea32d8'

    res = await parser.parse(hashes=[hash], out=out)
    print(res)


asyncio.get_event_loop().run_until_complete(main())

    # loop = asyncio.get_event_loop()
    # with PC() as pc:
    #     q = Queue()
    #
    #     q.put(Job(
    #         spider=TransactionSpider(
    #             vm=vm,
    #             net=net,
    #             module=module
    #         ),
    #         params={'mode': mode, 'hash': hash},
    #         item=Trace(),
    #         dao=dao
    #     ))
    #
    #     task = loop.create_task(pc.add_jobs(q))
    #     loop.run_until_complete(task)
    #
    #     task = loop.create_task(pc.run())
    #     loop.run_until_complete(task)



# import asyncio
# import csv
# import os
# from queue import Queue
#
# from tqdm import tqdm
#
# from dao.meta import JsonDao
# from item.evm.blk import Block
# from item.evm.sc import ABI
# from item.evm.tx import Transaction, Trace, Receipt
# from spider.evm.blk import BlockSpider
# from spider.evm.sc import ContractSpider
# from spider.evm.tx import TransactionSpider
# from utils.conf import Vm, Net, Module
# from utils.pc import Task, Job, PC
#
#
# async def main():
#     vm = Vm.EVM
#     output_dir = f'../out/{vm.value}'
#     label_fpath = 'out/label.csv'
#
#     hash_dict = {'eth': set(), 'bsc': set(), 'pol': set()}
#     with open(label_fpath, mode='r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             src, dst = row.get("Src"), row.get("Dst")
#             src_tx_hash = row.get("SrcTxHash")
#             dst_tx_hash = row.get("DstTxHash")
#
#             if dst != '' and dst_tx_hash != "":
#                 hash_dict[dst.lower()].add(dst_tx_hash)
#             hash_dict[src.lower()].add(src_tx_hash)
#
#     abi_contract_dict = {'eth': set(), 'bsc': set(), 'pol': set()}
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/tx"
#         for h in hash_dict.get(net.value):
#             rcpt_dao = JsonDao(fpath=f"{cur_dir}/{h}/rcpt.json")
#             trace_dao = JsonDao(fpath=f"{cur_dir}/{h}/trace.json")
#
#             rcpt, trace = None, None
#             for e in rcpt_dao.load(batch_size=1):
#                 if len(e) > 0:
#                     rcpt = e[0]
#             for e in trace_dao.load(batch_size=1):
#                 if len(e) > 0:
#                     trace = e[0]
#
#             addr_arr = []
#             if rcpt and trace:
#                 if rcpt.get("to_address", None):
#                     addr_arr.append(rcpt.get("to_address"))
#                 if rcpt.get('logs', None):
#                     for l in rcpt.get('logs'):
#                         if l.get("address", None):
#                             addr_arr.append(l.get("address"))
#
#                 for i in range(len(addr_arr)):
#                     if trace.get("array"):
#                         try:
#                             addr_arr[i] = next(
#                                 t["action"]["to_address"].lower()
#                                 for t in trace.get("array", [])
#                                 if (
#                                         t["action"].get("call_type") is not None
#                                         and t["action"].get("call_type", "").lower() == "delegatecall"
#                                         and t["action"]["from_address"].lower() == addr_arr[i].lower()
#                                 )
#                             )
#                         except StopIteration:
#                             pass
#                 abi_contract_dict[net.value].update(addr_arr)
#         print(f'{net.value} abi:', len(abi_contract_dict[net.value]))
#
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/sc"
#         with os.scandir(cur_dir) as entries:
#             for h in [entry.name for entry in entries if entry.is_dir()]:
#                 abi_dao = JsonDao(fpath=f"{cur_dir}/{h}/abi.json")
#                 if abi_dao.exist():
#                     abi_contract_dict[net.value].discard(h)
#         print(f'{net.value} abi:', len(abi_contract_dict[net.value]))
#     todo = []
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         for a in abi_contract_dict[net.value]:
#             todo.append({
#                 'net': net.value,
#                 'address': a.lower()
#             })
#
#     jobs = Queue()
#     for e in tqdm(todo):
#         address = e.get('address').lower()
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
#         module = Module.SC
#         job = Job([
#             Task(
#                 spider=ContractSpider(
#                     vm=vm,
#                     net=net,
#                     module=module
#                 ),
#                 params={'mode': m, 'address': address},
#                 item={'abi': ABI()}[m],
#                 dao=JsonDao(fpath=f"{output_dir}/{net.value}/{module.value}/{address}/{m}.json")
#             )
#             for m in ['abi']
#         ])
#         jobs.put(job)
#
#     pc = PC(jobs)
#     el = await pc.run(cp_ratio=8)
#     print(el)
# asyncio.get_event_loop().run_until_complete(main())


# async def main():
#     vm = Vm.EVM
#     output_dir = f'../out/{vm.value}'
#     label_fpath = 'out/label.csv'
#
#     hash_dict = {'eth': set(), 'bsc': set(), 'pol': set()}
#     with open(label_fpath, mode='r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             src, dst = row.get("Src"), row.get("Dst")
#             src_tx_hash = row.get("SrcTxHash")
#             dst_tx_hash = row.get("DstTxHash")
#
#             if dst != '' and dst_tx_hash != "":
#                 hash_dict[dst.lower()].add(dst_tx_hash)
#             hash_dict[src.lower()].add(src_tx_hash)
#
#     # for k, v in hash_dict.items():
#     #     print(k, len(v))
#
#     block_hash_dict = {'eth': set(), 'bsc': set(), 'pol': set()}
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/tx"
#         for h in hash_dict.get(net.value):
#             trans_dao = JsonDao(fpath=f"{cur_dir}/{h}/trans.json")
#             trans = [e for e in trans_dao.load(batch_size=1)][0][0]
#             block_hash = trans.get('block_hash').lower()
#             block_hash_dict[net.value].add(block_hash)
#         print(f'{net.value} block:', len(block_hash_dict[net.value]))
#
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/blk"
#         with os.scandir(cur_dir) as entries:
#             for h in [entry.name for entry in entries if entry.is_dir()]:
#                 block_dao = JsonDao(fpath=f"{cur_dir}/{h}/block.json")
#                 if block_dao.exist():
#                     block_hash_dict[net.value].discard(h)
#         print(f'{net.value} block:', len(block_hash_dict[net.value]))
#     todo = []
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         for h in block_hash_dict[net.value]:
#             todo.append({
#                 'net': net.value,
#                 'hash': h
#             })
#
#     jobs = Queue()
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
#         module = Module.BLK
#         job = Job([
#             Task(
#                 spider=BlockSpider(
#                     vm=vm,
#                     net=net,
#                     module=module
#                 ),
#                 params={'mode': m, 'hash': hash},
#                 item={'block': Block()}[m],
#                 dao=JsonDao(fpath=f"{output_dir}/{net.value}/{module.value}/{hash}/{m}.json")
#             )
#             for m in ['block']
#         ])
#         jobs.put(job)
#
#     pc = PC(jobs)
#     el = await pc.run(cp_ratio=8)
#     print(el)
# asyncio.get_event_loop().run_until_complete(main())


# async def main():
#     vm = Vm.EVM
#     output_dir = f'../out/{vm.value}'
#     label_fpath = 'out/label.csv'
#
#     hash_dict = {'eth': set(), 'bsc': set(), 'pol': set()}
#     with open(label_fpath, mode='r', newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             src, dst = row.get("Src"), row.get("Dst")
#             src_tx_hash = row.get("SrcTxHash")
#             dst_tx_hash = row.get("DstTxHash")
#
#             if dst != '' and dst_tx_hash != "":
#                 hash_dict[dst.lower()].add(dst_tx_hash)
#             hash_dict[src.lower()].add(src_tx_hash)
#
#     for k, v in hash_dict.items():
#         print(k, len(v))
#
#     todo = []
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/tx"
#         for h in hash_dict[net.value]:
#             # trans_dao = JsonDao(fpath=f"{cur_dir}/{h}/trans.json")
#             # trace_dao = JsonDao(fpath=f"{cur_dir}/{h}/trace.json")
#             rcpt_dao = JsonDao(fpath=f"{cur_dir}/{h}/rcpt.json")
#             if not rcpt_dao.exist():
#                 todo.append({
#                     'net': net.value,
#                     'hash': h
#                 })
#
#     jobs = Queue()
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
#             for m in ['rcpt']
#         ])
#         jobs.put(job)
#
#     pc = PC(jobs)
#     el = await pc.run(cp_ratio=4)
#     print(el)
# asyncio.get_event_loop().run_until_complete(main())


    # jobs = Queue()
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



# async def main():
#     vm = Vm.EVM
#     output_dir = f'../out/{vm.value}'
#
#     todo = []
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/tx"
#         with os.scandir(cur_dir) as entries:
#             for h in [entry.name for entry in entries if entry.is_dir()]:
#                 rcpt_dao = JsonDao(fpath=f"{cur_dir}/{h}/rcpt.json")
#                 trace_dao = JsonDao(fpath=f"{cur_dir}/{h}/trace.json")
#
#                 rcpt, trace = None, None
#                 for e in rcpt_dao.load(batch_size=1):
#                     if len(e) > 0:
#                         rcpt = e[0]
#                 for e in trace_dao.load(batch_size=1):
#                     if len(e) > 0:
#                         trace = e[0]
#
#                 addr_arr = []
#                 if rcpt and trace:
#                     if rcpt.get("to_address", None):
#                         addr_arr.append(rcpt.get("to_address"))
#                     if rcpt.get('logs', None):
#                         for l in rcpt.get('logs'):
#                             if l.get("address", None):
#                                 addr_arr.append(l.get("address"))
#
#                     for i in range(len(addr_arr)):
#                         if trace.get("array"):
#                             try:
#                                 addr_arr[i] = next(
#                                     t["action"]["to_address"].lower()
#                                     for t in trace.get("array", [])
#                                     if (
#                                             t["action"]["call_type"].lower() == "delegatecall"
#                                             and t["action"]["from_address"].lower() == addr_arr[i].lower()
#                                     )
#                                 )
#
#                             except StopIteration:
#                                 pass
#                     for a in addr_arr:
#                         todo.append({
#                             'net': net.value,
#                             'address': a.lower()
#                         })
#
#     jobs = Queue()
#     # abi
#     for e in tqdm(todo):
#         address = e.get('address').lower()
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
#         module = Module.SC
#         job = Job([
#             Task(
#                 spider=ContractSpider(
#                     vm=vm,
#                     net=net,
#                     module=module
#                 ),
#                 params={'mode': m, 'address': address},
#                 item={'abi': ABI()}[m],
#                 dao=JsonDao(fpath=f"{output_dir}/{net.value}/{module.value}/{address}/{m}.json")
#             )
#             for m in ['abi']
#         ])
#         jobs.put(job)
#
#     pc = PC(jobs)
#     await pc.run(cp_ratio=4)
# asyncio.get_event_loop().run_until_complete(main())


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


# async def main():
#     csv_fpath = "out/label.csv"
#     vm = Vm.EVM
#
#     todo = []
#     output_dir = f'../out/{vm.value}'
#
#     todo = []
#     for net in [Net.ETH, Net.BSC, Net.POL]:
#         cur_dir = f"{output_dir}/{net.value}/tx"
#         with os.scandir(cur_dir) as entries:
#             for h in [entry.name for entry in entries if entry.is_dir()]:
#                 dao = JsonDao(fpath=f"{cur_dir}/{h}/trans.json")
#                 for tx in dao.load(batch_size=1):
#                     if len(tx) > 0:
#                         todo.append({
#                             'net': net.value,
#                             'block_hash': tx[0].get('block_hash', '').lower()
#                         })
#
#     jobs = Queue()
#     # trans + trace + rcpt
#     for e in tqdm(todo):
#         hash = e.get('block_hash').lower()
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
#         module = Module.BLK
#         job = Job([
#             Task(
#                 spider=BlockSpider(
#                     vm=vm,
#                     net=net,
#                     module=module
#                 ),
#                 params={'mode': m, 'hash': hash},
#                 item={'block': Block()}[m],
#                 dao=JsonDao(fpath=f"{output_dir}/{net.value}/{module.value}/{hash}/{m}.json")
#             )
#             for m in ['block']
#         ])
#         jobs.put(job)
#
#     pc = PC(jobs)
#     await pc.run()
# asyncio.get_event_loop().run_until_complete(main())

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




