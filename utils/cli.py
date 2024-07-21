#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : cli.py
@Time   : 2024/7/14 21:48
@Author : zzYe

"""
import argparse

from utils.conf import Vm, Net, Module


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--module', choices=[
        'tx.trans', 'tx.trace', 'tx.rcpt',
        'blk.block', 'sc.abi', 'parse.trans', 'parse.sg'
    ], type=str, default='tx.trans')
    parser.add_argument('-h', '--hash', type=str, default='')
    parser.add_argument('-a', '--address', type=str, default='')
    parser.add_argument('-o', '--output', type=str, default='out/')

    args = parser.parse_args()



