#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : req.py
@Time   : 2024/7/9 15:57
@Author : zzYe

"""
import random

from settings import HEADERS_LIST


def get_headers():
    return {'User-Agent': random.choice(HEADERS_LIST)}
