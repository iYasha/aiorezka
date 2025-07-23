import asyncio

from aiorezka.api import RezkaAPI


async def main() -> None:
    async with RezkaAPI() as api:
        stream = await api.stream.get_series_stream(movie_id=59138, audio_track_id=56, season=2, episode=1)
        print(stream["1080p"]["hls"])


if __name__ == "__main__":
    asyncio.run(main())
