#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : ps.py
@Time   : 2024/7/16 11:44
@Author : zzYe

"""
from pydantic import Field

from item.meta import Item, check_source, snake_to_camel


class Input(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.hash = source.get('hash')
        self.func = source.get('func')
        self.args = source.get('args')
        return self

    hash: str = Field(default='')
    func: str = Field(default='')
    args: dict = Field(default={})


class EventLog(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.hash = source.get('hash')
        self.event = source.get('event')
        self.args = source.get('args')
        return self

    hash: str = Field(default='')
    event: str = Field(default='')
    args: dict = Field(default={})


class Timestamp(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.hash = source.get('hash')
        self.timestamp = source.get('timestamp')
        self.block_number = source.get('blockNumber')
        return self

    hash: str = Field(default='')
    timestamp: str = Field(default='')
    block_number: str = Field(default='')


class Subgraph(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.hash = source.get('hash')

        nodes, edges = set(), []
        for p in source.get('paths'):
            if not (p.get('from') in nodes and p.get('to') in nodes):
                edges.append(p)
            nodes.add(p.get('from'))
            nodes.add(p.get('to'))

        self.edges = list(edges)
        self.nodes = list(nodes)
        return self

    hash: str = Field(default='')
    edges: list = Field(default=[])
    nodes: list = Field(default=[])
