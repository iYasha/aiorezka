import asyncio
from functools import cached_property
from types import TracebackType
from typing import Dict, Optional, Type

import faker
from aiohttp import ClientResponse, ClientSession

import aiorezka
from aiorezka.backend.movie import RezkaMovie
from aiorezka.backend.movie_detail import RezkaMovieDetail
from aiorezka.cli import StatsThread
from aiorezka.utils import retry


def get_trailer_url(movie_id: int) -> dict:
    """
    Request:
    Url = https://hdrezka320fkk.org/engine/ajax/gettrailervideo.php
    Method = POST
    Content-type = multipart/form-data
    Body: id=65407
    Response example:
    {
        "success": true,
        "message": "Возникла неизвестная ошибка",
        "code": "<iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/jZZvQvqWiao?iv_load_policy=3&modestbranding=1&hd=1&rel=0&showinfo=0&autoplay=1\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen style=\"background: transparent; position: relative;\"></iframe>",
        "title": "&laquo;Меч короля&raquo; <small>(оригинальное название: \"Bastarden / The Promised Land\", 2023)</small>",
        "description": "Датский король отправляет своего лучшего рыцаря обуздать дикие земли, покуда простирается его длань. Но здесь, за стенами высоких замков, свои законы. Местные князья не спешат подчиняться королевскому наместнику. Они сами решают, кто будет возделывать их земли, а кто упокоится в них навсегда. Конфликт усугубляет прекрасная дева, обещанная отцом местному феодалу. Оставить её — значит потерять честь. Спасти — обречь себя на верную гибель. Но там, где опытный политик отступает, истинный рыцарь обнажает меч.",
        "link": "https://hdrezka320fkk.org/films/drama/65407-mech-korolya-2023.html"
    }
    """
    raise NotImplementedError()


class RezkaResponse(ClientResponse):
    async def read(self) -> bytes:
        body = await super().read()
        StatsThread.total_responses += 1
        return body


class RezkaSession(ClientSession):
    semaphore = asyncio.BoundedSemaphore(aiorezka.concurrency_limit)

    def __init__(self, *args, **kwargs) -> None:
        kwargs["response_class"] = RezkaResponse
        super().__init__(*args, **kwargs)

    @retry(
        retries=aiorezka.max_retry,
        delay=aiorezka.retry_delay,
    )
    async def _request(self, *args, **kwargs) -> ClientResponse:
        async with self.semaphore:
            return await super()._request(*args, **kwargs)


class RezkaAPI:
    host: str = aiorezka.host

    def __init__(
        self,
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.http_session = RezkaSession(raise_for_status=self.raise_for_status)
        self.fake = faker.Faker()
        self._headers = headers or {}

    @classmethod
    async def raise_for_status(cls, response: RezkaResponse) -> None:
        if not 200 <= response.status < 300:
            resp_content = await response.read()
            StatsThread.error_responses += 1
            # TODO: Create custom exception and use it inside retry decorator to display only reason and status
            raise Exception(
                f"Status: {response.status}\n" f"Reason: {response.reason}\n" f"Content: {resp_content}",
            )

    @property
    def fake_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self.fake.chrome(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,nl;q=0.5,und;q=0.4,fr;q=0.3,he;q=0.2",
            **self._headers,
        }

    @cached_property
    def movie(self) -> RezkaMovie:
        return RezkaMovie(self)

    @cached_property
    def movie_detail(self) -> RezkaMovieDetail:
        return RezkaMovieDetail(self)

    async def __aenter__(self) -> "RezkaAPI":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.http_session.close()
