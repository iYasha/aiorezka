import asyncio

import aiorezka
from aiorezka.api import RezkaAPI


async def main() -> None:
    async with RezkaAPI() as api:
        detailed_movies = await api.movie_detail.get(f"{aiorezka.host}/cartoons/comedy/2136-rik-i-morti-2013.html")
        print(detailed_movies.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
