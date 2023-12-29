import asyncio
import re
from typing import Any, Optional, Tuple

from aiorezka.logger import get_logger

logger = get_logger("aiorezka.utils.retry")


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
    exceptions: Tuple[Exception] = (Exception,),
) -> callable:
    def decorator(func: callable) -> callable:
        async def wrapper(*args, **func_kwargs) -> Any:  # noqa: ANN401
            for retry_no in range(retries):
                try:
                    return await func(*args, **func_kwargs)
                except exceptions as e:
                    if retry_no == retries - 1:
                        raise e
                    retry_delay = delay * (backoff ** (retry_no + 1))
                    logger.info(
                        f"Exception {e} occurred, retrying in {retry_delay} seconds. Retry {retry_no + 1}/{retries}",
                    )
                    await asyncio.sleep(retry_delay)

        return wrapper

    return decorator
