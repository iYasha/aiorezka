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


def get_quick_content(movie_id: int) -> dict:
    """
    Request:
    Url = https://hdrezka320fkk.org/engine/ajax/quick_content.php
    Method = POST
    Content-type = multipart/form-data
    Body: id=65415&is_touch=1
    Response example:
    <div class="b-content__catlabel films">
        <i class="entity">Фильм</i>
        <i class="icon"></i>
    </div>
    <div class="b-content__bubble_title">
        <a href="https://hdrezka320fkk.org/films/thriller/65415-sredi-volkov-2023.html">Среди волков</a>
    </div>
    <div class="b-content__bubble_rating">
        <span class="label">Рейтинг фильма:</span>
        <b>5.35</b>
        (23)

        <span class="b-rating">
            <span class="current" style="width: 53.5%;"></span>
        </span>
    </div>
    <div class="b-content__bubble_text">Брат и сестра, не видевшие друг друга много лет, оказываются вовлеченными в одно и то же ограбление по разные стороны баррикад: она — в качестве офицера полиции, он — в качестве преступника. Старые раны вновь напомнят о себе, брату и сестре придется сделать...
        </div>
    <div class="b-content__bubble_text">
        <span class="label">Жанр:</span>
        <a href="https://hdrezka320fkk.org/films/thriller/">Триллеры</a>
        , <a href="https://hdrezka320fkk.org/films/drama/">Драмы</a>
        , <a href="https://hdrezka320fkk.org/films/crime/">Криминал</a>
        , <a href="https://hdrezka320fkk.org/films/foreign/">Зарубежные</a>
    </div>
    <div class="b-content__bubble_str">
        <span class="label">Режиссер:</span>
        <span class="person-name-item" itemprop="director" itemscope itemtype="http://schema.org/Person" data-id="242583" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/242583-lida-patituchchi/" itemprop="url">
                <span itemprop="name">Лида Патитуччи</span>
            </a>
        </span>
    </div>
    <div class="b-content__bubble_str">
        <span class="label">В ролях:</span>
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="33559" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/33559-izabella-ragoneze/" itemprop="url">
                <span itemprop="name">Изабелла Рагонезе</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="189264" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/189264-andrea-arkandzheli/" itemprop="url">
                <span itemprop="name">Андреа Арканджели</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="431520" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/431520-karolina-mikelandzheli/" itemprop="url">
                <span itemprop="name">Каролина Микеланджели</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="431521" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/431521-aleksandr-gavranich/" itemprop="url">
                <span itemprop="name">Александр Гавранич</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="229103" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/229103-gennaro-di-colandrea/" itemprop="url">
                <span itemprop="name">Gennaro Di Colandrea</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="383321" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/383321-klara-posnett/" itemprop="url">
                <span itemprop="name">Клара Поснетт</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="9111" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/9111-klara-ponso/" itemprop="url">
                <span itemprop="name">Клара Понсо</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="113572" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/113572-alan-katich/" itemprop="url">
                <span itemprop="name">Алан Катич</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="57995" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/57995-milosh-timotievich/" itemprop="url">
                <span itemprop="name">Милош Тимотиевич</span>
            </a>
        </span>
        и
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="431522" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/431522-gabriele-portogeze/" itemprop="url">
                <span itemprop="name">Габриэле Портогезе</span>
            </a>
        </span>
    </div>
    <div class="b-content__bubble_rates">
        <span class="imdb">
            IMDb: <b>6.4</b>
            <i>(273)</i>
        </span>
    </div>
    """


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
        :param cache_rebuild: bool - rebuild cache on start in DiskCacheThreadProvider
        """
        self.http_session = RezkaSession(raise_for_status=self.raise_for_status)
        self.fake = faker.Faker()
        self._headers = headers or {}
        if aiorezka.use_cache:
            self.cache = QueryCache(aiorezka.cache_directory)
            self.cache_provider = DiskCacheThreadProvider(
                self.cache,
                do_cache_rebuild=kwargs.get("cache_rebuild", True),
            )

    @classmethod
    async def raise_for_status(cls, response: RezkaResponse) -> None:
        if not 200 <= response.status < 300:
            resp_content = await response.read()
            StatsThread.error_responses += 1
            # TODO: Create custom exception and use it inside retry decorator to display only reason and status
            is_service_unavailable = response.status == 503
            exception_message = (
                f"Url: {response.request_info.url}\nStatus: {response.status}\nReason: {response.reason}"
            )
            if not is_service_unavailable:
                exception_message += f"\nContent: {resp_content}"
            raise Exception(exception_message)

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
