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
        self._id = '{}-{}'.format(
            params.get("mode"),
            params.get("key")
        )

    @property
    def status(self):
        return self._status

    def set_status(self, status: Status):
        self._status = status

    @property
    def id(self):
        return self._id

    async def run(self):
        self._status = Status.RUNNING
        try:
            res = await self.spider.get(
                **self.params
            )
            source = res.get('res')
            if source is not None:
                self.item.map(source)
                self._status = Status.FINISHED
                return self.item
            else:
                self._status = Status.FAIL
        except Exception as e:
            self._status = Status.FAIL
        return None


class PC:
    def __init__(self, source: Queue[Job], cp_ratio: int = 8, maxsize: int = 8):
        """
        Four queue: Ready/Running/Finished/Fail

        :param maxsize:
        """
        self.re_q = Queue()
        self.ru_q = asyncio.Queue(maxsize=maxsize)
        self.fi_q = Queue()
        self.fa_q = Queue()

        if not(isinstance(cp_ratio, int) and cp_ratio >= 1):
            raise ValueError()
        self.cp_ratio = cp_ratio

        self.bf = BloomFilter(capacity=1_000_000, error_rate=0.001)
        self.wl, self.el = set(), set()

        while not source.empty():
            job = source.get()
            if job.id not in self.bf:
                self.re_q.put(job)
                self.bf.add(job.id)
                continue

            if job.id not in self.wl:
                self.re_q.put(job)
                self.wl.add(job.id)

        self._status = Status.READY
        self._count = 0

    async def producer(self):
        while self.re_q.qsize() != 0:
            job = self.re_q.get()
            await self.ru_q.put(job)

    async def consumer(self):
        while not (self.re_q.qsize() == 0 and self.ru_q.qsize() == 0):
            job = await self.ru_q.get()
            await job.run()

            if job.status == Status.FINISHED:
                self.fi_q.put(job)
            else:
                self.fa_q.put(job)
            self._count += 1

            if self._count % 1000 == 0:
                print(
                    f"The current count of completed jobs is: "
                    f"{self._count}."
                )

    async def run(self):
        self._status = Status.RUNNING
        print(
            f"Start executing, the total number of jobs is: "
            f"{self.re_q.qsize()}."
        )

        p_worker = asyncio.create_task(self.producer())
        c_workers = [
            asyncio.create_task(self.consumer())
            for _ in range(self.cp_ratio)
        ]
        workers = [p_worker] + c_workers
        await asyncio.gather(*workers)
        print(
            f"The current count of completed jobs is: "
            f"{self._count}."
        )
        self._status = Status.FINISHED


