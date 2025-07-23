import argparse
import asyncio

from aiorezka import __version__
from aiorezka.api import RezkaAPI


async def cli() -> None:
    parser = argparse.ArgumentParser(description="Aiorezka CLI")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=True,
        help="URL of the movie or TV series to download. Can be full URL or just urn (e.g. /films/series/12345.html)",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=".",
        type=str,
        help="Path to save downloaded files (default: current directory)",
    )
    parser.add_argument(
        "-s",
        "--season",
        type=int,
        required=True,
        help="Season number for TV series (default: 1)",
    )
    parser.add_argument(
        "-a",
        "--audio-track",
        type=str,
        required=True,
        help="Preferred audio track for TV series",
    )
    args = parser.parse_args()

    async with RezkaAPI() as api:
        await api.downloader.download_tv_series(args.url, args.path, args.audio_track, args.season)


if __name__ == "__main__":
    asyncio.run(cli())
