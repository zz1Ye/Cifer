#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : web3.py
@Time   : 2024/7/11 11:52
@Author : zzYe

"""
from typing import Dict, Any, Union, List

from hexbytes import HexBytes
from web3.datastructures import AttributeDict


def parse_hexbytes_dict(data: Dict[str, Any]) -> Union[Dict[str, str], List[Dict[str, str]], str]:
    if isinstance(data, AttributeDict):
        return {key: parse_hexbytes_dict(value) for key, value in dict(data).items()}
    if isinstance(data, dict):
        return {key: parse_hexbytes_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [parse_hexbytes_dict(item) for item in data]
    elif isinstance(data, (HexBytes, bytes)):
        return data.hex()
    else:
        return data