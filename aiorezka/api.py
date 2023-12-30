import asyncio
from functools import cached_property
from types import TracebackType
from typing import Dict, Optional, Type

import faker
from aiohttp import ClientResponse, ClientSession
from aiohttp.typedefs import StrOrURL

import aiorezka
from aiorezka.backend.movie import RezkaMovie
from aiorezka.backend.movie_detail import RezkaMovieDetail
from aiorezka.cache import DiskCacheThreadProvider, QueryCache
from aiorezka.cli import StatsThread
from aiorezka.utils import HTTPError, retry


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
    async def _request(
        self,
        method: str,
        str_or_url: StrOrURL,
        **kwargs,
    ) -> ClientResponse:
        async with self.semaphore:
            return await super()._request(method, str_or_url, **kwargs)


class RezkaAPI:
    host: str = aiorezka.host

    def __init__(
        self,
        *,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> None:
        """

        :param headers:
        :param rebuild_cache: bool - rebuild cache on start in DiskCacheThreadProvider
        :param request_params: dict - params for aiohttp.ClientSession.request
        """
        self.http_session = RezkaSession(raise_for_status=self.raise_for_status, **kwargs.get("request_params", {}))
        self.fake = faker.Faker()
        self._headers = headers or {}
        if aiorezka.use_cache:
            self.cache = QueryCache(aiorezka.cache_directory)
            self.cache_provider = DiskCacheThreadProvider(
                self.cache,
                cache_rebuild_on_start=kwargs.get("cache_rebuild_on_start", True),
            )

    @classmethod
    async def raise_for_status(cls, response: RezkaResponse) -> None:
        if not 200 <= response.status < 300:
            response_content = await response.read()
            StatsThread.error_responses += 1
            raise HTTPError(
                status_code=response.status,
                headers=response.headers,
                reason=response.reason,
                text=response_content.decode(),
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
        if aiorezka.use_cache:
            self.cache_provider.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if aiorezka.use_cache:
            self.cache_provider.stop().join()
        await self.http_session.close()
