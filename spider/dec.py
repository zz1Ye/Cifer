from queue import Queue
from typing import List, Dict

from dao.meta import Dao, JsonDao
from spider._meta import Spider, Result, Crawlable, Param
from spider.sched import Scheduler, Job, Task


class AsyncSpider(Spider):
    def __init__(self, spider: Crawlable, batch_jobs: int = 64):
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
                res_arr.append(job.result)
        return res_arr


class CacheSpider(Spider):
    def __init__(self, spider: Crawlable):
        super().__init__(spider.vm, spider.net)
        self.spider = spider
        self.module, self.mode = spider.module, spider.mode

    def dir_path(self, out: str, id: str):
        return '{}/{}/{}/{}/{}/{}.json'.format(
            out, self.vm.value, self.net.value,
            self.module.value, id, self.mode.value
        )

    async def parse(self, params: List[Param]) -> List[Result]:
        process_arr, id2item = [], dict()
        for p in params:
            _id, out = p.id, p.out
            dao = JsonDao(fpath=self.dir_path(out, _id))
            if dao and dao.exist():
                item = next(iter(dao.load()), [{}])[0]
                id2item[_id] = Result(key=_id, item=item)
                continue
            process_arr.append(p)
        process_arr = await self.spider.parse(process_arr)
        for e in process_arr:
            id2item[e.key] = e

        res_arr = []
        for p in params:
            e = id2item[p.id]
            res_arr.append(e)
            _id, out = p.id, p.out
            dao = JsonDao(fpath=self.dir_path(out, _id))
            if len(e.item) != 0 and dao and not dao.exist():
                dao.create()
                dao.insert(e.item)
        return res_arr
