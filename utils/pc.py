#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""       
@File   : pc.py
@Time   : 2024/7/11 17:44
@Author : zzYe

"""
import asyncio


class Job:
    def __init__(self, name, module, task):
        self.name = name
        self.module = module
        self.task = task


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

