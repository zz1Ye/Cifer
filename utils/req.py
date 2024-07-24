import random
from enum import Enum
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

