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
    READY = 'ready'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAIL = 'fail'


class Job:
    def __init__(
            self, spider: Spider, params: dict,
            item: Item, dao: Dao
    ):
        self.spider = spider
        self.params = params
        self.item = item
        self.dao = dao

        self._status = Status.READY
        self._id = '{}_{}_{}_{}'.format(
            self.spider.id,
            str(self.params),
            self.item.id,
            self.dao.id
        )

    @property
    def status(self):
        return self._status

    def set_status(self, status: Status):
        self._status = status

    @property
    def id(self):
        return self._id

    async def waiting(self):
        while True:
            if self._status in [
                Status.FINISHED,
                Status.FAIL
            ]:
                break
            await asyncio.sleep(1)
        return self.item

    async def run(self):
        self._status = Status.RUNNING
        try:
            res = await self.spider.get(**self.params)
            if res.get('res') is not None:
                self.item.map(res.get('res'))
                self.dao.create()
                self.dao.insert(self.item.dict())
                self._status = Status.FINISHED
            else:
                self._status = Status.FAIL
        except Exception as _:
            self._status = Status.FAIL


# class Job:
#     def __init__(self, tasks: List[Task]):
#         self._tasks = tasks
#         self._status = Status.READY
#         self._id = ",".join(sorted([t.id for t in tasks]))
#
#     @property
#     def tasks(self):
#         return self._tasks
#
#     @property
#     def status(self):
#         return self._status
#
#     @property
#     def id(self):
#         return self._id
#
#     async def run(self):
#         self._status = Status.RUNNING
#         todo_tasks = []
#         for t in self.tasks:
#             todo_tasks.append(asyncio.create_task(t.run()))
#         await asyncio.gather(*todo_tasks)
#         self._status = Status.FINISHED


class PC:
    def __init__(self, maxsize: int = 8):
        """
        Four queue: Ready/Running/Finished/Fail

        :param maxsize:
        """
        self.re_q = asyncio.Queue()
        self.ru_q = asyncio.Queue(maxsize=maxsize)
        self.fi_q = Queue()
        self.fa_q = Queue()

        # self.sq = Queue()
        # self.jq = asyncio.Queue(maxsize=maxsize)
        self.bf = BloomFilter(capacity=1_000_000, error_rate=0.001)
        self.wl, self.el = set(), set()
        self._status = Status.READY
        self._count = 0

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    def add_jobs(self, source: Queue[Job]):
        while not source.empty():
            job = source.get()
            if job.id not in self.bf:
                self.re_q.put(job)
                self.bf.add(job.id)
                continue

            if job.id not in self.wl:
                self.re_q.put(job)
                self.wl.add(job.id)

    def finish(self):
        self._status = Status.FINISHED

    async def producer(self):
        while self._status != Status.FINISHED:
            job = await self.re_q.get()
            await self.ru_q.put(job)
        # while self.sq.qsize() != 0:
        #     job = self.sq.get()
        #     await self.jq.put(job)

    async def consumer(self):
        while self._status != Status.FINISHED:
            job = await self.ru_q.get()
            await job.run()
            if job.status == Status.FINISHED:
                self.fi_q.put(job)

            if job.status == Status.FAIL:
                self.fa_q.put(job)
            self._count += 1

            if self._count % 1000 == 0:
                print(
                    f"The current count of completed jobs is: {self._count}."
                )

        # while True:
        #     if self.sq.empty() and self.jq.empty():
        #         break
        #     job = await self.jq.get()
        #     await job.run()
        #     for task in job.tasks:
        #         if task.status is Status.FAIL:
        #             self.el.add(task.id)
        #     self._count += 1
        #
        #     if self._count % 1000 == 0 or (self.sq.empty() and self.jq.empty()):
        #         print(
        #             f"The current count of completed jobs is: {self._count}."
        #         )

    async def run(self, cp_ratio: int = 8):
        self._status = Status.RUNNING
        print(
            f"Start executing, the total number of jobs is: {self.sq.qsize()}."
        )
        if not(isinstance(cp_ratio, int) and cp_ratio >= 1):
            raise ValueError()

        p_worker = asyncio.create_task(self.producer())
        c_workers = [
            asyncio.create_task(self.consumer())
            for _ in range(cp_ratio)
        ]
        workers = [p_worker] + c_workers
        await asyncio.gather(*workers)
        # return list(self.el)

