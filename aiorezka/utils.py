import asyncio
import base64
import re
from typing import Any, Dict, Literal, Optional, Tuple, Type, Union

from aiohttp.client_exceptions import ClientError
from aiohttp.web_exceptions import HTTPException

from aiorezka.logger import get_logger

logger = get_logger("aiorezka.utils.retry")


class HTTPError(HTTPException):
    def __init__(self, status_code: Optional[int] = None, **kwargs: any) -> None:
        self.status_code = status_code or self.status_code
        super().__init__(**kwargs)


def get_movie_id_from_url(movie_page_url: str) -> Optional[int]:
    assert movie_page_url is not None, "movie_page_url is required"
    match = re.search(r"\/(\d+)-", movie_page_url)
    if match:
        return int(match.group(1))
    return None


def retry(
    *,
    retries: int = 3,
    delay: int = 1,
    backoff: int = 2,
    exceptions: Tuple[Type[Exception]] = (ClientError,),
) -> callable:
    """
    Retry decorator with exponential backoff.

    :param retries: int - number of retries
    :param delay: int - delay in seconds
    :param backoff: int - backoff multiplier
    :param exceptions: tuple - exceptions to catch and retry. Default: (aiohttp.ClientError,) + (aiohttp.ClientResponseError, )
    :return: callable
    """

    handled_exceptions = exceptions + (HTTPException,)

    def decorator(func: callable) -> callable:
        async def wrapper(*args, **func_kwargs) -> Any:  # noqa: ANN401
            for retry_no in range(retries):
                try:
                    return await func(*args, **func_kwargs)
                except handled_exceptions as e:
                    if retry_no == retries - 1:
                        raise e
                    retry_delay = delay * (backoff ** (retry_no + 1))
                    if isinstance(e, HTTPException):
                        logger.info(
                            f"HTTPError {e.status_code} occurred, reason: {e.reason}, retrying in {retry_delay} seconds. Retry {retry_no + 1}/{retries}",
                        )
                        logger.debug(f"HTTPError occurred, response: {e.text}")
                    else:
                        logger.info(
                            f"Exception {e} occurred, retrying in {retry_delay} seconds. Retry {retry_no + 1}/{retries}",
                        )
                    await asyncio.sleep(retry_delay)

        return wrapper

    return decorator


class StreamDecoder:
    stream_separator = "//_//"
    trash_list = ["$$#!!@#!@##", "^^^!@##!!##", "####^!!##!@@", "@@@@@!##!^^^", "$$!!@$$@^!@#$$@"]

    @classmethod
    def _decode_stream_base64(cls, stream_encoded: str) -> str:
        stream_encoded = stream_encoded[2:]
        for _ in range(2):
            stream_encoded = stream_encoded.replace(cls.stream_separator, "")
            for value in cls.trash_list:
                stream_encoded = stream_encoded.replace(
                    base64.b64encode(value.encode()).decode(),
                    "",
                )
        return base64.b64decode(stream_encoded.encode()).decode()

    @classmethod
    def decode(cls, base64_encoded_stream_original: str) -> Dict[str, Dict[Union[Literal["hls", "mp4"]], str]]:
        if base64_encoded_stream_original is None:
            raise ValueError("base64_encoded_stream_original cannot be None")
        try:
            base64_decoded_stream = cls._decode_stream_base64(base64_encoded_stream_original)
        except Exception as e:
            raise Exception(base64_encoded_stream_original) from e
        split_by_quality = base64_decoded_stream.split(",")
        quality_pattern = re.compile(r"^\[\d+p(?:\s\w*)?\]")
        streams = {}
        for stream in split_by_quality:
            re_quality_results = quality_pattern.findall(stream)
            if not re_quality_results:
                continue
            quality = re_quality_results[0].replace("[", "").replace("]", "")
            stream_urls_str = stream.replace(re_quality_results[0], "")
            try:
                stream_urls = map(
                    str.strip,
                    stream_urls_str.split(
                        " or ",
                    ),
                )
                mp4_stream = next(filter(lambda x: x.endswith(".mp4"), stream_urls), None)
                streams[quality] = {
                    "hls": mp4_stream + ":hls:manifest.m3u8",
                    "mp4": mp4_stream,
                }
            except Exception as e:
                raise Exception(stream_urls_str) from e
        return streams
