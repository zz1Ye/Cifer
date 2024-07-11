#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : sg.py
@Time   : 2024/7/11 11:18
@Author : zzYe

"""
from typing import List

from item.evm.tx import Transaction, Trace


class SubgraphParser:
    def __init__(self):
        pass

    def parse(self, trans: Transaction, traces: List[Trace]):
        res = [
            {'from': trans.from_address},
            {'to': trans.to_address}
        ]

        for t in traces:
            res.append({
                'from': t.action.from_address,
                'to': t.action.to_address
            })

        return res
