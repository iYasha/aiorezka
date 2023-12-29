import asyncio
import os
import pickle
import string
import threading
import time
from typing import Optional

import aiorezka
from aiorezka.logger import get_logger

try:
    import aiofiles
except ImportError:
    raise ImportError("You need to install aiofiles to use cache.")


class TTLObject:
    __slots__ = ("value", "expired_at", "from_disk")

    def __init__(self, value: any, ttl: int, from_disk: bool = False) -> None:
        self.value = value
        self.expired_at = time.time() + ttl
        self.from_disk = from_disk

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expired_at


class QueryCache:
    garbage = str.maketrans({x: "_" for x in string.punctuation})
    memcache_size = aiorezka.memcache_max_len
    cache_ttl = aiorezka.cache_ttl
    logger = get_logger("aiorezka.cache.QueryCache")

    def __init__(self, disk_cache_path: str) -> None:
        self.disk_cache_path = disk_cache_path
        if not os.path.exists(self.disk_cache_path):
            os.makedirs(self.disk_cache_path)
        self.cache = {}
        self.expired_cache = set()  # TODO: maybe we should rename it to cache_to_remove?

    def remove_garbage(self, query: str) -> str:
        return query.translate(self.garbage).lower()

    async def set(self, key: str, value: any) -> None:
        self.cache[self.remove_garbage(key)] = TTLObject(value, self.cache_ttl)

    async def get(self, key: str, default: any = None) -> any:
        # check if cache marked as expired by previous request
        if key in self.expired_cache:
            return default

        cache_key = self.remove_garbage(key)
        item = self.cache.get(cache_key)

        # if cache not in memory, try to get it from disk
        if not item:
            item = await self.search_in_disk_cache(cache_key)
            if item is None:
                return default
            self.cache[cache_key] = item

        # if cache doesn't exist even in disk, return default
        if item is None:
            return default

        # if cache exists but expired, delete it from memory and disk
        if item.is_expired:
            del self.cache[cache_key]
            if item.from_disk:
                self.expired_cache.add(cache_key)
            return default

        return item.value

    async def search_in_disk_cache(self, cache_key: str) -> Optional[TTLObject]:
        cache_path = os.path.join(self.disk_cache_path, cache_key)
        if not os.path.exists(cache_path):
            return None
        async with aiofiles.open(cache_path, "rb") as f:
            try:
                item = pickle.loads(await f.read())
                item.from_disk = True  # mark cache as loaded from disk to prevent it from saving to disk again
                return item
            except Exception as e:
                self.logger.error(f"Error while loading cache from disk: {e}\nCache path: {cache_path}")
                self.expired_cache.add(cache_key)
                return None


class DiskCacheThreadProvider(threading.Thread):
    metadata_extension = ".metadata"
    logger = get_logger("aiorezka.cache.DiskCacheThreadProvider")

    def __init__(self, cache: QueryCache, *, do_cache_rebuild: bool = True) -> None:
        super().__init__()
        self.cache = cache

        self.stop_flag = threading.Event()
        self.sleep = threading.Event()

        self.already_stored = set()
        self.do_cache_rebuild = do_cache_rebuild

    async def store_metadata(self, cache_key: str, value: TTLObject) -> None:
        metadata_path = os.path.join(self.cache.disk_cache_path, f"{cache_key}{self.metadata_extension}")
        async with aiofiles.open(metadata_path, "w") as f:
            try:
                await f.write(str(value.expired_at))
            except Exception as e:
                self.logger.error(
                    f"Error while storing metadata to disk: {e}\nMetadata path: {metadata_path}",
                )

    async def store_cache_to_disk(self, cache_key: str, value: TTLObject) -> None:
        async with aiofiles.open(os.path.join(self.cache.disk_cache_path, cache_key), "wb") as f:
            await f.write(pickle.dumps(value))
        self.already_stored.add(cache_key)

    @staticmethod
    def _get_event_loop() -> asyncio.AbstractEventLoop:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if str(e).startswith("There is no current event loop in thread"):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise e
        return loop

    def remove_expired_cache(self) -> None:
        for cache_key in self.cache.expired_cache:
            cache_path = os.path.join(self.cache.disk_cache_path, cache_key)
            metadata_path = os.path.join(self.cache.disk_cache_path, f"{cache_key}{self.metadata_extension}")
            if os.path.exists(cache_path):
                os.remove(cache_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
        self.cache.expired_cache.clear()

    @classmethod
    async def check_if_expired_and_remove(
        cls,
        now: float,
        metadata_path: str,
        semaphore: asyncio.BoundedSemaphore,
    ) -> Optional[str]:
        async with semaphore:
            async with aiofiles.open(metadata_path, "r") as f:
                try:
                    expired_at = float(await f.read())
                except Exception as e:
                    cls.logger.error(
                        f"Error while loading metadata from disk: {e}\nMetadata path: {metadata_path}",
                    )
                    expired_at = None
        if expired_at is None or not now > expired_at:
            return
        cache_path = metadata_path.replace(cls.metadata_extension, "")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        os.remove(metadata_path)

    def cache_rebuild(self, loop: asyncio.AbstractEventLoop) -> None:
        semaphore = asyncio.BoundedSemaphore(aiorezka.max_open_files)

        now = time.time()
        tasks = []
        for cache_file in os.listdir(self.cache.disk_cache_path):
            if not cache_file.endswith(self.metadata_extension):
                continue
            cache_path = os.path.join(self.cache.disk_cache_path, cache_file)
            tasks.append(self.check_if_expired_and_remove(now, cache_path, semaphore))
        loop.run_until_complete(asyncio.gather(*tasks))
        self.logger.info(f"[Memcache] Cache rebuilded in {time.time() - now:.2f} seconds!")

    def run(self) -> None:
        loop = self._get_event_loop()
        # TODO: Here is a bug. If cache rebuild takes more time than Main Thread will be executed, then no items will be stored on disk.
        if self.do_cache_rebuild:
            self.cache_rebuild(loop)
        while not self.stop_flag.is_set():
            self.sleep.wait(timeout=10)
            self.remove_expired_cache()
            tasks = []
            memcache_size = len(self.cache.cache)
            _items_to_store = 0
            for key, value in self.cache.cache.items():
                if key in self.already_stored or value.from_disk:
                    continue
                _items_to_store += 1
                tasks.append(self.store_cache_to_disk(key, value))
                tasks.append(self.store_metadata(key, value))
            loop.run_until_complete(asyncio.gather(*tasks))
            self.logger.info(f"[Memcache] {_items_to_store} items stored!")
            if memcache_size > self.cache.memcache_size:
                self.cache.cache.clear()
                self.logger.info(f"[Memcache] Flushing memcache! {memcache_size} items flushed!")

    def stop(self) -> "DiskCacheThreadProvider":
        self.stop_flag.set()
        self.sleep.set()
        return self
