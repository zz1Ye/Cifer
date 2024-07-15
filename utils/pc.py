#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : pc.py
@Time   : 2024/7/11 17:44
@Author : zzYe

"""
import asyncio
from enum import Enum
from queue import Queue
from typing import List

from pybloom import BloomFilter

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

        self._id = '{}_{}_{}'.format(
            self.spider.__class__.__qualname__,
            str(self.params),
            self.item.__class__.__qualname__,
            self.dao.__class__.__qualname__
        )

    def set_status(self, status: Status):
        self.status = status

    @property
    def id(self):
        return self._id

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
        self.status = Status.Ready
        self._id = ",".join(sorted([t.id for t in tasks]))

    @property
    def id(self):
        return self._id

    async def run(self):
        self.status = Status.Running
        todo_tasks = []
        for t in self.tasks:
            todo_tasks.append(asyncio.create_task(t.run()))
        await asyncio.gather(*todo_tasks)
        self.status = Status.Finished


class PC:
    def __init__(self, source: Queue[Job], maxsize: int = 8):
        self.sq = Queue()
        self.jq = asyncio.Queue(maxsize=maxsize)
        self.bf = BloomFilter(capacity=1_000_000, error_rate=0.001)
        self.wl = set()
        self.count = 0

        while not source.empty():
            job = source.get()
            if job.id not in self.bf:
                self.sq.put(job)
                self.bf.add(job.id)
                continue

            if job.id not in self.wl:
                self.sq.put(job)
                self.wl.add(job.id)

    async def producer(self):
        while self.sq.qsize() != 0:
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
                print(f"The current count of completed jobs is: {self.count}.")

    async def run(self, cp_ratio: int = 2):
        print(f"Start executing, the total number of jobs is: {self.sq.qsize()}.")
        if not(isinstance(cp_ratio, int) and cp_ratio >= 1):
            raise ValueError()

        p_worker = asyncio.create_task(self.producer())
        c_workers = [
            asyncio.create_task(self.consumer())
            for _ in range(cp_ratio)
        ]
        workers = [p_worker] + c_workers
        await asyncio.gather(*workers)

