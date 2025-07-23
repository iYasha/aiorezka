import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Optional
from urllib.parse import urljoin

from yt_dlp import YoutubeDL

from aiorezka.logger import get_logger

if TYPE_CHECKING:
    from aiorezka.api import RezkaAPI


class RezkaDownloader:
    logger = get_logger("aiorezka.backend.downloader")

    def __init__(self, api_client: "RezkaAPI") -> None:
        self.api_client = api_client

    @classmethod
    def get_episodes_in_directory(cls, path: str) -> list[str]:
        episodes = []
        for file in os.listdir(path):
            if file.endswith(".mp4"):
                try:
                    episode = int(file.split("_")[1].split(".")[0])
                    episodes.append(episode)
                except (IndexError, ValueError):
                    continue
        return sorted(episodes)

    @classmethod
    def download_hls(cls, hls_url: str, episode: int, path_to_save: str, max_retries: int = 3) -> Optional[int]:
        def hook(d: dict) -> None:
            if d["status"] == "downloading":
                cls.logger.info(f'[Episode #{episode}] Downloading: {d["_percent_str"]} at {d["_speed_str"]}')
            elif d["status"] == "finished":
                cls.logger.info(f"[Episode #{episode}] Done downloading, now post-processing ...")
            elif d["status"] == "error":
                error_msg = d.get("error") or d.get("filename") or "Unknown error"
                cls.logger.info(f"[Episode #{episode}] Download error: {error_msg}")
            else:
                cls.logger.info(f"[Episode #{episode}] {d}")

        ydl_opts = {
            "outtmpl": f"{path_to_save}/ep_{episode}.%(ext)s",
            "remux_video": "mp4",
            "external_downloader": "aria2c",
            "external_downloader_args": {
                "aria2c": ["-x16", "-j16"],
            },
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [hook],
        }

        for attempt in range(1, max_retries + 1):
            try:
                cls.logger.info(f"[Episode #{episode}] Starting download attempt {attempt}...")
                with YoutubeDL(ydl_opts) as ydl:
                    result = ydl.download([hls_url])

                if result == 0:
                    cls.logger.info(f"[Episode #{episode}] Download succeeded on attempt {attempt}")
                    return None
                else:
                    cls.logger.warning(f"[Episode #{episode}] Download failed with code {result} on attempt {attempt}")

            except Exception as e:
                cls.logger.error(f"[Episode #{episode}] Download error on attempt {attempt}: {e}")

            if attempt < max_retries:
                wait_time = 5
                cls.logger.info(f"[Episode #{episode}] Retrying after {wait_time} seconds...")
                time.sleep(wait_time)

        cls.logger.error(f"[Episode #{episode}] All {max_retries} attempts failed.")
        return episode

    async def download_tv_series(self, url: str, path_to_save: str, audio_track_name: str, season: int) -> None:
        """
        Download a movie/tv series from the given URL and save it to the specified path.

        :param url: The URL of the file to download.
        :param path_to_save: The local path where the file will be saved.
        :param audio_track_name: audio track name.
        :param season: season number for series.
        """
        if url.startswith("http"):
            full_url = url
        else:
            full_url = urljoin(self.api_client.host, url)

        tv_series = await self.api_client.movie_detail.get(full_url)
        audio_track = next(
            filter(lambda track: track.audio_track_name == audio_track_name, tv_series.audio_tracks),
            None,
        )
        if not audio_track:
            self.logger.error(f"No audio track {audio_track_name} found for {full_url}")
            return

        path_to_save = os.path.join(path_to_save, tv_series.title)
        os.makedirs(path_to_save, exist_ok=True)

        downloaded_episodes = self.get_episodes_in_directory(path_to_save)
        episodes = await self.api_client.stream.get_episodes(
            tv_series.movie_id,
            audio_track.audio_track_id,
            season=season,
        )
        episodes_to_download = []

        for episode in episodes:
            if episode in downloaded_episodes:
                self.logger.info(f"Episode {episode} already downloaded, skipping.")
                continue

            streams = await self.api_client.stream.get_series_stream(
                movie_id=tv_series.movie_id,
                audio_track_id=audio_track.audio_track_id,
                season=season,
                episode=episode,
            )
            stream = streams.get("1080p Ultra", None) or streams.get("1080p", None)
            if not stream:
                self.logger.error(f"No stream found in 1080p for episode {episode} of {tv_series.title}")
                continue
            episodes_to_download.append((stream["hls"], episode, path_to_save))

        cannot_download_episodes = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(self.download_hls, url, ep, path) for url, ep, path in episodes_to_download]

            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    cannot_download_episodes.append(result)

        if cannot_download_episodes:
            self.logger.error("Failed to download the following episodes:")
            for episode in cannot_download_episodes:
                self.logger.error(f"Episode {episode} could not be downloaded to {path_to_save}")
