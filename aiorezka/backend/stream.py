import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Union
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

import aiorezka
from aiorezka.logger import get_logger
from aiorezka.utils import StreamDecoder

if TYPE_CHECKING:
    from aiorezka.api import RezkaAPI


class RezkaStream:
    logger = get_logger("aiorezka.backend.stream")
    series_base_urn: str = "/ajax/get_cdn_series/"

    def __init__(self, api_client: "RezkaAPI") -> None:
        self.api_client = api_client

    async def _get_cache(self, url: str, form_data: str) -> Any:  # noqa: ANN401
        if not aiorezka.use_cache:
            return None
        key = f"{url}?{form_data}"
        return await self.api_client.cache.get(key)

    async def _request_cdn_series(self, movie_id: int, audio_track_id: int, season: int, episode: int) -> dict:
        url = urljoin(aiorezka.host, self.series_base_urn)
        form_data = urlencode(
            {
                "id": movie_id,
                "translator_id": audio_track_id,
                "season": season,
                "episode": episode,
                "action": "get_episodes",
            },
        )
        resp = await self._get_cache(url, form_data)
        if resp:
            self.logger.debug(
                "Cache hit for movie_id=%s, audio_track_id=%s, season=%s, episode=%s",
                movie_id,
                audio_track_id,
                season,
                episode,
            )
            return resp

        self.logger.debug(
            "Getting series stream for movie_id=%s, audio_track_id=%s, season=%s, episode=%s\nURL: %s",
            movie_id,
            audio_track_id,
            season,
            episode,
            url,
        )
        async with self.api_client.http_session.post(
            url,
            headers={**self.api_client.fake_headers, "Content-Type": "application/x-www-form-urlencoded"},
            params={
                "t": round(datetime.now(tz=timezone.utc).timestamp()),
            },
            data=form_data,
        ) as response:
            resp = json.loads(await response.text())
            if not resp.get("success"):
                raise Exception(f"Failed to get stream: {resp}")
            if aiorezka.use_cache:
                await self.api_client.cache.set(f"{url}?{form_data}", resp)
            return resp

    async def get_episodes(self, movie_id: int, audio_track_id: int, season: int) -> List[int]:
        data = await self._request_cdn_series(movie_id, audio_track_id, season, 1)
        episodes_html = data.get("episodes")
        if not episodes_html:
            return []
        return [
            int(x.get("data-episode_id"))
            for x in BeautifulSoup(episodes_html, "html.parser").find_all("li", class_="b-simple_episode__item")
        ]

    async def get_series_stream(
        self,
        movie_id: int,
        audio_track_id: int,
        season: int,
        episode: int,
    ) -> Dict[str, Dict[Union[Literal["hls", "mp4"]], str]]:
        data = await self._request_cdn_series(movie_id, audio_track_id, season, episode)
        if not data["success"]:
            raise Exception(f"Failed to get stream: {data['error']}")
        return StreamDecoder.decode(data["url"])
