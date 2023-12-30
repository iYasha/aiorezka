import asyncio
import itertools
from typing import TYPE_CHECKING, List, Optional, Tuple, Union
from urllib.parse import urlencode

from aiorezka.enums import GenreType, MovieFilter
from aiorezka.factories import MovieFactory
from aiorezka.schemas import Movie

if TYPE_CHECKING:
    from aiorezka.api import RezkaAPI


class RezkaMovie:
    base_urn: str = "/page/%d"

    def __init__(self, api_client: "RezkaAPI") -> None:
        self.base_url = f"{api_client.host}{self.base_urn}"
        self.api_client = api_client

    async def iter_pages(
        self, page_range: range, *, chain: bool = False, **kwargs
    ) -> Union[Tuple[List[Movie], ...], itertools.chain[Movie]]:
        tasks = []
        for page_id in page_range:
            tasks.append(self.get_page(page_id, **kwargs))
        task_results = await asyncio.gather(*tasks)
        if chain:
            return itertools.chain(*task_results)
        return task_results

    async def get_page(
        self,
        page_id: int,
        *,
        movie_filter: MovieFilter = MovieFilter.LATEST,
        genre: Optional[GenreType] = None,
    ) -> List[Movie]:
        params = {"filter": movie_filter.value}
        if genre:
            params["genre"] = genre.value
        encoded_params = "?" + urlencode(params) if params else ""
        async with self.api_client.http_session.get(
            (self.base_url % page_id) + encoded_params,
            headers=self.api_client.fake_headers,
        ) as response:
            html = await response.text()
        return MovieFactory(html).movies
