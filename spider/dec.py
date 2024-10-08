from queue import Queue
from typing import List

from dao.meta import JsonDao
from spider.meta import Spider, Result, Crawlable, Param
from spider.sched import Scheduler, Job, Task


class AsyncSpider(Spider):
    def __init__(self, spider: Crawlable, batch_jobs: int = 16):
        super().__init__(spider.vm, spider.net)
        self.module, self.mode = spider.module, spider.mode
        self.spider = spider
        self.batch_jobs = batch_jobs

    async def parse(self, params: List[Param]) -> List[Result]:
        res_arr = []
        for i in range(0, len(params), self.batch_jobs):
            source = Queue()
            for e in params[i: i+self.batch_jobs]:
                source.put(Job(e.id, [Task(e.id, self.spider, e)]))

            sched = Scheduler(source)
            queue = await sched.run()
            while not queue.empty():
                job = queue.get()
                res_arr += job.result[0]
        return res_arr


class CacheSpider(Spider):
    def __init__(self, spider: Crawlable, batch_size: int = 64):
        super().__init__(spider.vm, spider.net)
        self.spider = spider
        self.batch_size = batch_size
        self.module, self.mode = spider.module, spider.mode

    def dir_path(self, out: str, id: str):
        return '{}/{}/{}/{}/{}/{}.json'.format(
            out, self.vm.value, self.net.value,
            self.module.value, id, self.mode.value
        )

    async def parse(self, params: List[Param]) -> List[Result]:
        todo_params, id2item = [], dict()
        for p in params:
            _id, out = p.id, p.out
            dao = JsonDao(fpath=self.dir_path(out, _id))
            if dao and dao.exist():
                item = next(iter(dao.load()), [{}])[0]
                id2item[_id] = Result(key=_id, item=item)
                continue
            todo_params.append(p)

        for i in range(0, len(todo_params), self.batch_size):
            batch_params = todo_params[i: i+self.batch_size]
            process_arr = await self.spider.parse(batch_params)
            for e in process_arr:
                id2item[e.key] = e

            for p in batch_params:
                e = id2item[p.id]
                _id, out = p.id, p.out
                dao = JsonDao(fpath=self.dir_path(out, _id))
                if len(e.item) != 0 and dao and not dao.exist():
                    dao.create()
                    dao.insert(e.item)

        return [id2item[p.id] for p in params]
