#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : data.py
@Time   : 2024/7/18 15:19
@Author : zzYe

"""


def snake_to_camel(snake: str):
    if snake is None or snake == "":
        return

    words = snake.split('_')
    return words[0] + ''.join(x.title() for x in words[1:])


def snake_keys_to_camel(_dict: dict):
    n_dict = {}
    for k, v in _dict.items():
        n_k = snake_to_camel(k)
        if isinstance(v, dict):
            n_dict[n_k] = snake_keys_to_camel(v)
        elif isinstance(v, list):
            n_dict[n_k] = [
                snake_keys_to_camel(e) if isinstance(e, dict) else e
                for e in v]
        else:
            n_dict[n_k] = v
    return n_dict
