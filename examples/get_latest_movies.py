import asyncio

from aiorezka.api import RezkaAPI


async def main() -> None:
    async with RezkaAPI() as api:
        movies = await api.movie.iter_pages(range(1, 10), chain=True)
        for movie in movies:
            print(f"{movie.title} - {movie.page_url}")


if __name__ == "__main__":
    asyncio.run(main())
