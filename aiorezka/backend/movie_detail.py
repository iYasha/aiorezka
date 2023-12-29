import asyncio
from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple

import aiorezka
from aiorezka.factories import MovieDetailFactory
from aiorezka.schemas import Movie, MovieDetail

if TYPE_CHECKING:
    from aiorezka.api import RezkaAPI


class RezkaMovieDetail:
    def __init__(self, api_client: "RezkaAPI") -> None:
        self.api_client = api_client

    async def many(self, movies: Iterable[Movie]) -> Tuple[MovieDetail]:
        tasks = []
        for movie in movies:
            tasks.append(self.get(movie.page_url))
        return await asyncio.gather(*tasks)

    async def many_from_urls(self, movie_urls: List[str] = None) -> Iterable[MovieDetail]:
        tasks = []
        for movie_url in movie_urls:
            tasks.append(self.get(movie_url))
        return await asyncio.gather(*tasks)

    async def _get_cache(self, movie_page_url: str) -> Optional[MovieDetail]:
        if not aiorezka.use_cache:
            return None
        return await self.api_client.cache.get(movie_page_url)

    async def get(self, movie_page_url: str) -> Optional[MovieDetail]:
        item = await self._get_cache(movie_page_url)
        if item:
            return item
        async with self.api_client.http_session.get(
            movie_page_url,
            headers=self.api_client.fake_headers,
        ) as response:
            html = await response.text()
        factory = MovieDetailFactory(movie_page_url, html)
        item = MovieDetail.from_factory(factory)
        if aiorezka.use_cache:
            await self.api_client.cache.set(movie_page_url, item)
        return item
