# aiorezka

## Installation

### Without cache
```bash
pip install aiorezka
```

### With cache
_It's recommended to use cache, because it will reduce load on Rezka API._

```bash
pip install aiorezka[request_cache]
```

## Usage
```python
from aiorezka.api import RezkaAPI
import asyncio

async def main():
    async with RezkaAPI() as api:
        details = await api.movie_detail.get(
            'https://rezka.ag/cartoons/comedy/2136-rik-i-morti-2013.html'
        )
        print(details)

asyncio.run(main())
```
You can find more examples in [examples](examples) directory.

## Configuration
### Hostname configuration
You can configure hostname for requests. By default it will use `rezka.ag` hostname.
To change it, you can pass environment variable `REZKA_HOSTNAME` or change it in code:
```python 
import aiorezka

aiorezka.host = 'rezka.co'
```

### Concurrency configuration
You can configure concurrency for API client, basically it will limit number of concurrent requests via asyncio.Semaphore.
By default it will use 60 concurrent requests.
To change it, you can pass environment variable `REZKA_CONCURRENCY_LIMIT` or change it in code:
```python
import aiorezka

aiorezka.concurrency_limit = 100
```

### Retry configuration
You can configure retry policy for requests. By default it will retry 3 times with 1 * (backoff ** retry_no) second delay.
To change it, you can pass environment variables, such as `REZKA_MAX_RETRY` and `REZKA_RETRY_DELAY` or change it in code:
```python
import aiorezka

aiorezka.max_retry = 5
aiorezka.retry_delay = 2
```

### Cache configuration
You can configure cache for requests. By default, it will use `aiorezka.cache.QueryCache` + `aiorezka.cache.DiskCacheThreadProvider` with 1 day TTL.
Cache will periodically save to disk, so you can use it between restarts.


#### use_cache
Enable or disable cache. By default, it's disabled.
```python
import aiorezka

aiorezka.use_cache = False  # disable cache
```
or use environment variable `REZKA_USE_CACHE`

#### cache_directory
Directory where cache will be stored. By default, it's `/tmp/aiorezka_cache`.
```python
import aiorezka

aiorezka.cache_directory = '/tmp/aiorezka_cache'
```
or use environment variable `REZKA_CACHE_DIRECTORY`

#### memcache_max_len
Max number of items in memory cache. When it's reached, it will be saved to disk. 

By default, it's 1000.
```python
import aiorezka

aiorezka.memcache_max_len = 1000
```
or use environment variable `REZKA_MEMCACHE_MAX_LEN`

#### cache_ttl
TTL for cache objects.

By default, it's 1 day.
```python
import aiorezka

aiorezka.cache_ttl = 60 * 60 * 24  # 1 day
```
or use environment variable `REZKA_CACHE_TTL`

#### max_open_files
Max number of open files for cache. It's used for `aiorezka.cache.DiskCacheThreadProvider`. When app starts cache will be rebuilt on disk, so it will open a lot of files to check if they are expired.

By default, it's 5000.
```python
import aiorezka

aiorezka.max_open_files = 5000
```
or use environment variable `REZKA_MAX_OPEN_FILES`

You can disable cache rebuild on start, then TTL will be ignored.
```python
from aiorezka.api import RezkaAPI

async def main():
    async with RezkaAPI(cache_rebuild_on_start=False) as api:
        pass
```

### Logging configuration
You can configure logging for aiorezka. By default, it will use `logging.INFO` level.
```python
import aiorezka

aiorezka.log_level = "DEBUG"
```
or use environment variable `REZKA_LOG_LEVEL`

## Debugging
### Measure RPS
Measure requests per second, use it only for debug purposes.
```python
import asyncio

from aiorezka.api import RezkaAPI
from aiorezka.cli import measure_rps


@measure_rps
async def main():
    async with RezkaAPI() as api:
        movies = await api.movie.iter_pages(range(1, 10), chain=True)
        detailed_movies = await api.movie_detail.many(movies)
        for movie in detailed_movies:
            attributes = '\n'.join([f'{attr["key"]}: {attr["value"]}' for attr in movie.attributes])
            print(f'{movie.title}\n{attributes}\n')

if __name__ == '__main__':
    asyncio.run(main())
```
Output will look like:
```bash
[main][333 requests in 37.82s] 8.81 rps
```
