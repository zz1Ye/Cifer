from typing import List

from pydantic import Field

from item.meta import Item, check_source, snake_to_camel


class CompleteForm(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.tx = source.get('tx')
        self.timestamp = source.get('timestamp')
        self.subgraph = source.get('subgraph')
        self.input = source.get('input')
        self.event_logs = source.get('event_logs')
        return self

    tx: dict = Field(default={})
    timestamp: str = Field(default='')
    subgraph: dict = Field(default={})
    input: dict = Field(default={})
    event_logs: dict = Field(default={})


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
        self.address = source.get('address')
        self.event = source.get('event')
        self.args = source.get('args')
        return self

    hash: str = Field(default='')
    address: str = Field(default='')
    event: str = Field(default='')
    args: dict = Field(default={})


class EventLogs(Item):
    @snake_to_camel
    @check_source
    def map(self, source: dict):
        array = []
        for e in source.get('array', []):
            element = EventLog()
            element.map(e)
            array.append(element)
        self.array = array
        return self

    array: List[EventLog] = Field(default=[])


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
        if 'edges' in source and 'nodes' in source:
            self.edges = source.get('edges')
            self.nodes = source.get('nodes')
            return self

        nodes, edges = set(), []
        for p in source.get('paths', []):
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


class FundsFlowSubgraph(Item):
    class _Node(Item):
        @snake_to_camel
        @check_source
        def map(self, source: dict):
            self.nid = source.get('nid')
            return self
        nid: str = Field(default='')

    class _Edge(Item):
        @snake_to_camel
        @check_source
        def map(self, source: dict):
            self.from_ = source.get('from')
            self.to_ = source.get('to')
            self.attributes = source.get('attributes')
            return self

        from_: str = Field(default='')
        to_: str = Field(default='')
        attributes: dict = Field(default={})

    @snake_to_camel
    @check_source
    def map(self, source: dict):
        self.hash = source.get('hash')
        self.edges = [
            self._Edge().map(e)
            for e in source.get('edges', [])
        ]
        self.nodes = [self._Node().map({'nid': _id}) for _id in source.get('nodes', [])]
        return self

    hash: str = Field(default='')
    edges: list = Field(default=[])
    nodes: list = Field(default=[])
