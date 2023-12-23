from functools import cached_property
from typing import Dict, Optional

import faker
from aiohttp import ClientSession

from aiorezka.backend.latest_movie import RezkaLatestMovie
from aiorezka.backend.movie_detail import RezkaMovieDetail
import aiorezka


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


class RezkaAPI:
    host: str = aiorezka.host

    def __init__(
        self,
        http_session: ClientSession,
        *,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.fake = faker.Faker()
        self.http_session = http_session
        self._headers = headers or {}

    @classmethod
    def is_success(cls, status_code: int) -> bool:
        return 200 <= status_code < 300

    @property
    def fake_headers(self):
        return {
            'User-Agent': self.fake.chrome(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,nl;q=0.5,und;q=0.4,fr;q=0.3,he;q=0.2',
            **self._headers,
        }

    @cached_property
    def latest(self) -> RezkaLatestMovie:
        return RezkaLatestMovie(self)

    @cached_property
    def detail(self) -> RezkaMovieDetail:
        return RezkaMovieDetail(self)
