from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel

from aiorezka.attributes import BaseAttribute
from aiorezka.enums import MovieType

if TYPE_CHECKING:
    from aiorezka.factories import MovieDetailFactory


class Movie(BaseModel):
    id: int
    title: str
    poster_preview_url: str
    additional_information: str
    page_url: str
    cover_text: str


class MovieSeason(BaseModel):
    season_no: int
    season_name: str


class AudioTrack(BaseModel):
    audio_track_id: int
    audio_track_name: str


class FranchiseRelatedMovie(BaseModel):
    movie_id: int
    title: str
    franchise_index: int
    release_year: str
    rating: Optional[float] = None
    movie_page_url: str


class MovieDetail(BaseModel):
    movie_id: int
    default_audio_track: Optional[int] = None
    title: str
    title_en: Optional[str] = None
    poster_url: str
    description: Optional[str] = None
    movie_type: MovieType
    attributes: List[BaseAttribute]
    seasons: List[MovieSeason]
    audio_tracks: List[AudioTrack]
    franchise_related_movies: List[FranchiseRelatedMovie]

    class Config:
        json_encoders = {
            BaseAttribute: lambda v: v.to_dict(),
        }

    @classmethod
    def from_factory(cls, factory: "MovieDetailFactory") -> "MovieDetail":
        return MovieDetail(
            movie_id=factory.movie_id,
            default_audio_track=factory.default_audio_track,
            title=factory.title,
            title_en=factory.title_en,
            poster_url=factory.poster_url,
            description=factory.description,
            movie_type=factory.movie_type,
            attributes=factory.attributes,
            seasons=factory.seasons,
            audio_tracks=factory.available_audio_tracks,
            franchise_related_movies=factory.franchise_related_movies,
        )
