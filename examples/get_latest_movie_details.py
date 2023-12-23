import asyncio

from aiorezka.api import RezkaAPI
from aiorezka.cli import measure_rps


@measure_rps
async def main() -> None:
    async with RezkaAPI() as api:
        movies = await api.movie.iter_pages(range(1, 10), chain=True)
        detailed_movies = await api.movie_detail.many(movies)
        for movie in detailed_movies:
            attributes = "\n".join([f'{attr["key"]}: {attr["value"]}' for attr in movie.attributes])
            print(f"{movie.title}\n{attributes}\n")


if __name__ == "__main__":
    asyncio.run(main())
