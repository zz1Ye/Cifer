#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ps.py
@Time   : 2024/7/16 11:44
@Author : zzYe

"""
from pydantic import Field

from item.meta import Item


class Input(Item):
    def map(self, source: dict):
        if source is None or not isinstance(source, dict):
            return

        self.func = source.get('func')
        self.args = source.get('args')

    func: str = Field(default='')
    args: dict = Field(default={})


class EventLog(Item):
    def map(self, source: dict):
        if source is None or not isinstance(source, dict):
            return

        self.event = source.get('event')
        self.args = source.get('args')

    event: str = Field(default='')
    args: dict = Field(default={})


class Timestamp(Item):
    def map(self, source: dict):
        if source is None or not isinstance(source, dict):
            return

        self.timestamp = source.get('timestamp')
        self.block_number = source.get('blockNumber')

    timestamp: str = Field(default='')
    block_number: str = Field(default='')


class Subgraph(Item):
    def map(self, source: dict):
        if source is None or not isinstance(source, dict):
            return

        self.edges = source.get('edges')
        self.nodes = source.get('nodes')

    edges: list = Field(default=[])
    nodes: list = Field(default=[])
