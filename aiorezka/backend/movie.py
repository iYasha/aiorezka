import asyncio
import itertools
from typing import TYPE_CHECKING, List, Optional, Tuple, Union
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from aiorezka.enums import GenreType, MovieFilter
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

    @staticmethod
    def get_movies_from_page(page_html: str) -> List[Movie]:
        # TODO: Move to factory
        soup = BeautifulSoup(page_html, "html.parser")
        movies = []
        for movie in soup.find(attrs={"class": "b-content__inline_items"}).find_all(
            attrs={"class": "b-content__inline_item"},
        ):
            cover_section = movie.find(attrs={"class": "b-content__inline_item-cover"})
            link_section = movie.find(attrs={"class": "b-content__inline_item-link"})
            movie_link_url_tag = link_section.find("a")

            movies.append(
                Movie(
                    id=movie.get("data-id"),
                    title=movie_link_url_tag.text.strip(),
                    poster_preview_url=cover_section.find("img").get("src"),
                    additional_information=link_section.find("div").text.strip(),
                    page_url=movie_link_url_tag.get("href"),
                    cover_text=cover_section.text.strip(),
                ),
            )
        return movies

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
            return self.get_movies_from_page(html)
