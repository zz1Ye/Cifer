import logging
from enum import Enum, auto


class Status(Enum):
    READY = auto()
    RUNNING = auto()
    FINISHED = auto()


class Job:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.result = None
        self.status = Status.READY

    async def start(self):
        raise NotImplementedError()

    async def run(self):
        self.status = Status.RUNNING
        try:
            self.result = await self.start()
        except Exception as e:
            logging.error(e)
        self.status = Status.FINISHED


class Scheduler:
    def __init__(self):
        pass

    def add_job(self, job: Job):
        pass


