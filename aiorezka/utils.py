import re
from typing import Optional, Tuple


def get_movie_id_from_url(movie_page_url: str) -> Optional[int]:
    assert movie_page_url is not None, 'movie_page_url is required'
    match = re.search(r'\/(\d+)-', movie_page_url)
    if match:
        return int(match.group(1))
    return None
