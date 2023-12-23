import re
from functools import cached_property
from typing import List, Tuple, Optional, Dict

from bs4 import BeautifulSoup

from aiorezka.enums import MovieType
from aiorezka.schemas import AudioTrack, MovieSeason, FranchiseRelatedMovie
from aiorezka.utils import get_movie_id_from_url


class MovieDetailFactory:
    re_player_initializer = re.compile(
        r'sof\.tv\.(initCDNMoviesEvents|initCDNSeriesEvents)\((\d+),\s?(\d+),'
    )

    def __init__(self, page_url: str, raw_html: str):
        self.page_url = page_url
        self.raw_html = raw_html
        self.soup = BeautifulSoup(raw_html, 'html.parser')

        self.movie_id, self.default_audio_track = self._movie_id_and_default_audio_track

    @cached_property
    def title(self) -> str:
        return self.soup.find(attrs={'class': 'b-post__title'}).text.strip()

    @cached_property
    def title_en(self) -> Optional[str]:
        title_en = self.soup.find(attrs={'class': 'b-post__origtitle'})
        return title_en.text.strip() if title_en else None

    @cached_property
    def movie_type(self) -> MovieType:
        movie_type = self.soup.find('meta', attrs={'property': 'og:type'}).get('content').strip()
        return MovieType.FILM if movie_type == 'video.movie' else MovieType.SERIES

    @cached_property
    def description(self) -> Optional[str]:
        description = self.soup.find(attrs={'class': 'b-post__description_text'})
        return description.text.strip() if description else None

    @cached_property
    def poster_url(self) -> str:
        return self.soup.find(attrs={'class': 'b-post__infotable_left'}).find('img').get('src')

    @cached_property
    def franchise_related_movies(self) -> List[FranchiseRelatedMovie]:
        # get franchise related movies
        franchise_related_movies_table = self.soup.find(attrs={'class': 'b-post__partcontent'})
        franchise_related_movie_items = franchise_related_movies_table.find_all(
            attrs={'class': 'b-post__partcontent_item'}
        ) if franchise_related_movies_table else []

        franchise_related_movies = []
        for movie in franchise_related_movie_items:
            title_block = movie.find(attrs={'class': 'title'})

            # Example: <a href="https://hdrezka320fkk.org/films/fiction/23757-chelovek-pauk-vozvraschenie-domoy-2017.html">Человек-паук: Возвращение домой</a>
            franchise_title = title_block.text.strip()
            if 'current' in movie.get('class'):
                movie_page_url = self.page_url
            else:
                movie_page_url = title_block.find('a').get('href')

            franchise_movie_id = get_movie_id_from_url(movie_page_url)

            franchise_related_movies.append(
                FranchiseRelatedMovie(
                    movie_id=franchise_movie_id,
                    title=franchise_title,
                    movie_page_url=movie_page_url,

                    # Example: 16
                    franchise_index=int(movie.find(attrs={'class': 'num'}).text.strip()),

                    # Example: 2017 год
                    release_year=movie.find(attrs={'class': 'year'}).text.split(' ')[0].strip(),

                    # Example: 7.16
                    rating=float(movie.find(attrs={'class': 'rating'}).text.strip()),
                )
            )

        return franchise_related_movies

    @cached_property
    def attributes(self) -> List[Dict[str, str]]:
        # get attributes from table
        attributes = []
        for attr_group in self.soup.find(attrs={'class': 'b-post__info'}).find_all('tr'):
            key = attr_group.find(attrs={'class': 'l'})
            value = attr_group.text
            if key:
                value = value.replace(key.text, '')
            attributes.append(
                {
                    'key': key.text.strip().replace(':', '', 1) if key else None,
                    'value': value.strip(),
                }
            )
        return attributes

    @cached_property
    def available_audio_tracks(self) -> List[AudioTrack]:
        # get available audio tracks
        audio_tracks_table = self.soup.find(attrs={'id': 'translators-list'})
        return [
            {'audio_track_id': x.get('data-translator_id'), 'audio_track_name': x.text.strip()}
            for x in audio_tracks_table.find_all('li')
        ] if audio_tracks_table else []

    @cached_property
    def seasons(self) -> List[MovieSeason]:
        # get seasons
        season_tab = self.soup.find(attrs={'id': 'simple-seasons-tabs'})
        return [
            {'season_no': x.get('data-tab_id'), 'season_name': x.text.strip()}
            for x in season_tab.find_all('li')
        ] if season_tab else []

    @cached_property
    def _movie_id_and_default_audio_track(self) -> Tuple[int, Optional[int]]:
        # get movie_id and default_audio_track from player initializer
        cdn_params = self.re_player_initializer.findall(self.raw_html)
        if cdn_params:
            _, movie_id, default_audio_track = cdn_params[0]
            return int(movie_id), int(default_audio_track)
        else:
            return get_movie_id_from_url(self.page_url), None
