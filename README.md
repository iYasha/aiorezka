# aiorezka

## Installation

```bash
pip install aiorezka
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
