#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : pc.py
@Time   : 2024/7/11 17:44
@Author : zzYe

"""
import asyncio
import hashlib
from enum import Enum
from queue import Queue
from typing import List

from dao.meta import Dao
from item.meta import Item
from spider.meta import Spider


class Status(Enum):
    Ready = 'ready'
    Running = 'running'
    Finished = 'finished'


class Task:
    def __init__(
            self, spider: Spider, params: dict,
            item: Item, dao: Dao
    ):
        self.spider = spider
        self.params = params
        self.item = item
        self.dao = dao
        self.status = Status.Ready

        _id = '{}_{}_{}'.format(
            self.spider.__class__.__qualname__,
            str(self.params),
            self.item.__class__.__qualname__,
            self.dao.__class__.__qualname__
        )
        self._uid = hashlib.sha256(_id.encode()).hexdigest()[:64]

    def set_status(self, status: Status):
        self.status = status

    @property
    def uid(self):
        return self._uid

    async def run(self):
        origin = self.item.dict()
        try:
            self.status = Status.Running
            res = await self.spider.get(**self.params)
            if res.get('res') is not None:
                self.item.map(res.get('res'))
                if self.dao.create():
                    self.dao.insert(self.item.dict())
            self.status = Status.Finished
        except Exception as _:
            self.item.map(origin)
            self.status = Status.Ready


class Job:
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks
        self.point = 0
        self.status = Status.Ready

    async def run(self):
        self.status = Status.Running
        while self.point < len(self.tasks):
            cur = self.cur_task()
            await cur.run()
            self.switch_task()

    def cur_task(self):
        if self.point < len(self.tasks):
            return self.tasks[self.point]
        self.status = Status.Finished
        return None

    def switch_task(self):
        if self.point < len(self.tasks):
            self.tasks[self.point].set_status(
                Status.Finished
            )
            self.point += 1
        if self.point == len(self.tasks):
            self.status = Status.Finished


class PC:
    def __init__(self, source: Queue[Job], maxsize: int = 64):
        self.sq = source
        self.jq = asyncio.Queue(maxsize=maxsize)
        self.count = 0

    async def producer(self):
        while True and self.sq.qsize() != 0:
            job = self.sq.get()
            await self.jq.put(job)

    async def consumer(self):
        while True:
            if self.sq.empty() and self.jq.empty():
                break
            job = await self.jq.get()
            await job.run()
            self.count += 1

            if self.count % 1000 == 0 or (self.sq.empty() and self.jq.empty()):
                print(f"The current count of completed jobs is: {self.count}")

    async def run(self):
        p_worker = asyncio.create_task(self.producer())
        c_worker = asyncio.create_task(self.consumer())
        workers = [p_worker, c_worker]
        await asyncio.gather(*workers)

