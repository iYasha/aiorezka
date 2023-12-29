import asyncio

from aiorezka.api import RezkaAPI


async def main() -> None:
    async with RezkaAPI() as api:
        movies = await api.movie.iter_pages(range(1, 5), chain=True)
        detailed_movies = await api.movie_detail.many(movies)
        for movie in detailed_movies:
            print(movie.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
