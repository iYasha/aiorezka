from typing import TYPE_CHECKING, List, Iterable, Optional

from aiorezka.factories import MovieDetailFactory
from aiorezka.schemas import MovieDetail

if TYPE_CHECKING:
    from aiorezka.api import RezkaAPI


class RezkaMovieDetail:

    def __init__(self, api_client: 'RezkaAPI'):
        self.api_client = api_client

    async def many(self, movie_urls: List[str]) -> Iterable[MovieDetail]:
        for movie_url in movie_urls:
            yield await self.get(movie_url)

    async def get(self, movie_page_url: str) -> Optional[MovieDetail]:
        async with self.api_client.http_session.get(
            movie_page_url,
            headers=self.api_client.fake_headers
        ) as response:
            if not self.api_client.is_success(response.status):
                return None
            html = await response.text()
            factory = MovieDetailFactory(movie_page_url, html)
            return MovieDetail.from_factory(factory)
