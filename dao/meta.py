import json
import logging
import os
import sys
from typing import Generator, List

import ijson


class Dao:
    def __init__(self, fpath: str):
        self.fpath = fpath

    def create(self) -> bool:
        raise NotImplementedError()

    def insert(self, data: dict) -> bool:
        raise NotImplementedError()

    def load(self, batch_size: int = 1024) -> Generator[List[dict], None, None]:
        raise NotImplementedError()

    def exist(self) -> bool:
        return os.path.isfile(self.fpath)

    def drop(self) -> bool:
        try:
            os.remove(self.fpath)
        except (FileNotFoundError, PermissionError, OSError) as e:
            logging.error(e)
            return False
        return True


class JsonDao(Dao):
    def __init__(self, fpath: str):
        super().__init__(fpath)

    def create(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
            with open(self.fpath, 'w') as _:
                pass

        except Exception as e:
            logging.error(e)
            return False

        return True

    def load(self, batch_size: int = 1024) -> Generator[List[dict], None, None]:
        with open(self.fpath, 'r', encoding='utf-8') as file:
            if file.read(1) == '':
                return
            file.seek(0)

            objects = ijson.items(file, 'item')

            buffer = []
            for obj in objects:
                buffer.append(obj)

                if len(buffer) == batch_size:
                    yield buffer
                    buffer = []

            if buffer:
                yield buffer

    def insert(self, data: dict) -> bool:
        rows = [
            r for batch in self.load(batch_size=1024) for r in batch
        ]
        rows.append(data)

        with open(self.fpath, 'w', encoding='utf-8') as file:
            json.dump(
                rows,
                file, ensure_ascii=False, indent=4
            )

        return True

    def delete(self, filter_params: dict) -> bool:
        rows = [
            r for batch in self.load(batch_size=1024) for r in batch
            if not all(
                r.get(k) == v
                for k, v in filter_params.items()
            )
        ]

        with open(self.fpath, 'w', encoding='utf-8') as file:
            json.dump(
                rows,
                file, ensure_ascii=False, indent=4
            )

        return True

    def query(self, filter_params: dict, limit: int = sys.maxsize) -> List[dict]:
        rows = []

        for batch in self.load(batch_size=1024):
            rows.extend([
                r for r in batch
                if all(
                    r.get(k) == v
                    for k, v in filter_params.items()
                )
            ])

            if len(rows) >= limit:
                break

        return rows[:limit]

    def update(self, filter_params: dict, new_data: dict) -> bool:
        rows = [
            r for batch in self.load(batch_size=1024) for r in batch
        ]
        for i in range(len(rows)):
            if all(
                rows[i].get(k) == v
                for k, v in filter_params.items()
            ):
                rows[i].update(
                    {k: v for k, v in new_data.items() if k in rows[i]}
                )

        with open(self.fpath, 'w', encoding='utf-8') as file:
            json.dump(
                rows,
                file, ensure_ascii=False, indent=4
            )

        return True
