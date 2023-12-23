from enum import Enum


class MovieType(str, Enum):
    FILM = "film"
    SERIES = "series"


class GenreType(int, Enum):
    FILM = 1
    SERIES = 2
    CARTOONS = 3
    ANIME = 82


class MovieFilter(str, Enum):
    LATEST = "last"
    POPULAR = "popular"
    SOON = "soon"
    WATCHING_NOW = "watching"
