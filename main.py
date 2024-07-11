#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : main.py
@Time   : 2024/7/11 16:31
@Author : zzYe

"""
import asyncio
import csv

import aiohttp
from tqdm import tqdm


if __name__ == '__main__':
    csv_fpath = "out/label.csv"

    todo = []
    with open(csv_fpath, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            src = row.get("Src")
            src_tx_hash = row.get("SrcTxHash")
            dst = row.get("Dst")
            dst_tx_hash = row.get("DstTxHash")

            todo.append({
                'vm': 'evm', 'net': src.lower(),
                'hash': src_tx_hash.lower()
            })
            if dst != '':
                todo.append({
                    'vm': 'evm', 'net': dst.lower(),
                    'hash': dst_tx_hash.lower()
                })

    for e in tqdm(todo):
        pass

