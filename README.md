# aiorezka

## Installation

```bash
pip install aiorezka
```

## Usage/Examples

```python
from aiorezka.api import RezkaAPI
from aiohttp import ClientSession
import asyncio

async def main():
    async with ClientSession() as session:
        datails = await RezkaAPI(session).detail.get(
            'https://rezka.ag/cartoons/comedy/2136-rik-i-morti-2013.html'
        )
        print(datails)

asyncio.run(main())
