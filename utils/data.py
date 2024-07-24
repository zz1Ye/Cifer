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


def snake_keys_to_camel(_object):
    if isinstance(_object, dict):
        return {
            snake_to_camel(k): snake_keys_to_camel(v)
            for k, v in _object.items()
        }

    if isinstance(_object, list):
        return [
            snake_keys_to_camel(e)
            for e in _object
        ]

    return _object
