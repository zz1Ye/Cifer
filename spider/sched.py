import asyncio
import logging
from enum import Enum, auto
from queue import Queue
from typing import List

from pybloom import BloomFilter

from spider.meta import Spider


class Status(Enum):
    READY = auto()
    RUNNING = auto()
    FINISHED = auto()


class Task:
    def __init__(self, task_id: str, spider: Spider, param: dict):
        self.id = task_id
        self.spider = spider
        self.param = param
        self.result = None
        self.status = Status.READY

    async def run(self):
        self.status = Status.RUNNING
        try:
            self.result = await self.spider.parse(**self.param)
        except Exception as e:
            logging.error(e)
        self.status = Status.FINISHED
        return self.result


class Job:
    def __init__(self, job_id: str, tasks: List[Task]):
        self.id = job_id
        self.tasks = tasks
        self.result = None
        self.status = Status.READY

    async def start(self):
        tasks = [
            asyncio.create_task(t.run())
            for t in self.tasks
        ]
        self.result = await asyncio.gather(*tasks)
        return self.result


class Scheduler:
    def __init__(self, source: Queue[Job], cp_ratio: int = 2, maxsize: int = 8):
        """
        One queue: Source
        Three queue: Ready/Running/Finished
        """
        self.sr_q = Queue()
        self.re_q = Queue()
        self.ru_q = asyncio.Queue(maxsize=maxsize)
        self.fi_q = Queue()

        if not (isinstance(cp_ratio, int) and cp_ratio >= 1):
            raise ValueError()
        self.cp_ratio = cp_ratio

        self.bf = BloomFilter(capacity=1_000_000, error_rate=0.001)
        self.wl, self.el = set(), set()

        while not source.empty():
            job = source.get()
            self.sr_q.put(job)
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
            assert job.status == Status.FINISHED
            self.fi_q.put(job.res)
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
        return self.sr_q


