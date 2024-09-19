from queue import Queue
from typing import List, Dict

from spider._meta import Spider, Result
from spider.sched import Scheduler, Job, Task


class AsyncSpider(Spider):
    def __init__(self, spider: Spider, batch_jobs: int = 64):
        super().__init__(spider.vm, spider.net)
        self.spider = spider
        self.batch_jobs = batch_jobs

    async def parse(self, params: List[Dict]) -> List[Result]:
        res_arr = []
        for i in range(0, len(params), self.batch_jobs):
            source = Queue()
            for e in params[i: i+self.batch_jobs]:
                source.put(Job(e['_id'], [Task(e['_id'], self.spider, e)]))

            sched = Scheduler(source)
            queue = await sched.run()
            while not queue.empty():
                job = queue.get()
                res_arr.append(job.result)
        return res_arr


class CacheSpider(Spider):
    def __init__(self, spider: Spider):
        super().__init__(spider.vm, spider.net)
        self.spider = spider

    async def parse(self, params: List[Dict]) -> List[Result]:
        process_arr, id2item = [], dict()
        for p in params:
            _id, dao = p.get("_id"), p.get("dao")
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
            e = id2item[p.get("_id")]
            res_arr.append(e)
            dao = p.get("dao")
            if len(e.item) != 0 and dao and not dao.exist():
                dao.create()
                dao.insert(e.item)
        return res_arr
