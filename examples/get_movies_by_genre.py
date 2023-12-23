import asyncio

from aiorezka.api import RezkaAPI
from aiorezka.enums import GenreType


async def main() -> None:
    async with RezkaAPI() as api:
        movies = await api.movie.iter_pages(range(1, 10), genre=GenreType.SERIES)
        for page_number, movies in enumerate(movies):
            for movie in movies:
                print(f"[{page_number}] {movie.title} - {movie.page_url}")


if __name__ == "__main__":
    asyncio.run(main())
