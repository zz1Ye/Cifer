#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : data.py
@Time   : 2024/7/18 15:19
@Author : zzYe

"""
import re


def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_dict_keys(data):
    new_data = {}
    for key, value in data.items():
        new_key = snake_to_camel(key)
        new_data[new_key] = value
    return new_data
