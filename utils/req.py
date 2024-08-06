import random
from enum import Enum
from typing import List
from urllib.parse import urlencode, urljoin

from pydantic import BaseModel


class Method(Enum):
    GET = "GET"
    POST = "POST"


class Url(BaseModel):
    domain: str
    params: dict

    def get(self):
        domain = self.domain if self.domain.endswith('/') else self.domain + '/'
        query = urlencode(self.params)

        return urljoin(
            domain, '?' + query
        )


class Headers(BaseModel):
    accept: str
    content_type: str
    user_agents: list

    def get(self):
        return {**{
            k.replace('_', '-'): v
            for k, v in self.dict().items()
            if k != 'user_agents'
        }, 'user-agent': random.choice(self.user_agents)}


class RPCNode(BaseModel):
    domain: str
    keys: list

    def get_key(self):
        return random.choice(self.keys)

    def get(self):
        d = self.domain if self.domain.endswith('/') else self.domain + '/'
        k = self.get_key()
        return '{}{}'.format(d, k)


class Request(BaseModel):
    url: str
    method: str
    headers: dict
    payload: dict


def get_random_user_agent(user_agents):
    return random.choice(user_agents)


class Result:
    def __init__(self, key, item: dict):
        self.key = key
        self.item = item


class ResultQueue:
    def __init__(self, queue: List[Result] = None):
        if queue is None:
            queue = []
        self.queue = queue
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.queue):
            result = self.queue[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, index):
        return self.queue[index]

    def __setitem__(self, index, value):
        self.queue[index] = value

    def __len__(self):
        return len(self.queue)

    def add(self, element: Result):
        self.queue.append(element)

    def get_none_idx(self):
        return [
            i
            for i, e in enumerate(self.queue)
            if e.item is None
        ]

    def get_non_none_idx(self):
        return [
            i
            for i, e in enumerate(self.queue)
            if e.item is not None
        ]
