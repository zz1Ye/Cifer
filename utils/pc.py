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
            self.item.map(res)
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

    queue = asyncio.Queue()

    def __init__(self):
        pass

    async def consumer(self):
        while True:
            item = await self.queue.get()
            self.queue.task_done()

    async def producer(num_workers, jobs):
        for i in range(num_workers):
            worker = asyncio.create_task(consumer(self.queue))
        # 将作业分配给消费者
        for job in jobs:
            await queue.put(job)
        # 通知所有消费者没有更多的作业
        for _ in range(num_workers):
            queue.put(None)
        await queue.join()  # 等待所有任务完成

    async def pc(self):
        # 假设 source_of_tasks 是一个异步迭代器，不断产生新的爬虫任务
        source_of_tasks = some_async_iterable_of_transaction_hashes()

        # 创建生产者任务
        producer_task = asyncio.create_task(producer(queue, session, source_of_tasks))

        # 创建消费者任务
        consumers = [asyncio.create_task(consumer(queue, session)) for _ in range(5)]

        # 等待生产者任务完成
        await producer_task

        # 等待队列中的所有任务被处理
        await queue.join()

        # 取消消费者任务
        for consumer in consumers:
            consumer.cancel()

