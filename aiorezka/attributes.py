import abc
from collections import namedtuple
from functools import cached_property
from typing import Dict, Generator, List, Type, TypeVar, Union

from bs4 import BeautifulSoup, Tag

_T = TypeVar("_T")

RezkaPerson = namedtuple("RezkaPerson", ["person_id", "name", "url", "photo_url"])
RezkaLink = namedtuple("RezkaLink", ["url", "title"])


class AttributeParseError(ValueError):
    pass


class BaseAttribute:
    __slots__ = ("original_name", "value_tag")
    _attr_name: str = None

    def __init__(self, name: str, value: Union[str, Tag]) -> None:
        self.original_name = name
        if isinstance(value, str):
            self.value_tag = BeautifulSoup(value, "html.parser")
        else:
            self.value_tag = value

    @abc.abstractmethod
    def value(self) -> any:
        pass

    def __str__(self) -> str:
        attr_name = getattr(self, "_attr_name", None)
        return f"<{self.__class__.__name__} name={attr_name} original_name={self.original_name} value={self.value}>"

    def __repr__(self) -> str:
        return str(self)

    def representation(self, original_name: bool = False) -> str:
        attr_name = self.original_name if original_name else getattr(self, "_attr_name", None)
        return f"{attr_name}: {self.value}"

    @classmethod
    def __get_validators__(cls) -> Generator[Type[_T], None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: "BaseAttribute" = None, *args, **kwargs) -> "BaseAttribute":
        return v

    def to_dict(self) -> Dict[str, any]:
        return {
            getattr(self, "_attr_name", self.original_name): self.value,
        }


class TextAttribute(BaseAttribute):
    @cached_property
    def value(self) -> str:
        return self.value_tag.text.strip()


class IntAttribute(TextAttribute):
    @cached_property
    def value(self) -> int:
        return int(super().value)


class RatingAttribute(BaseAttribute):
    @cached_property
    def value(self) -> Dict[str, float]:
        ratings = self.value_tag.find_all("span")
        if not ratings:
            raise AttributeParseError(f"No ratings found in {self.value_tag}")
        return {
            ratings[x].text.split(":")[0].strip(): float(ratings[x + 1].text.strip()) for x in range(0, len(ratings), 2)
        }


class TopListAttribute(BaseAttribute):
    @cached_property
    def value(self) -> List[str]:
        return [x.text.strip() for x in self.value_tag.find_all("a")]


class PersonAttribute(BaseAttribute):
    @cached_property
    def value(self) -> List[RezkaPerson]:
        persons = self.value_tag.find_all("span", attrs={"class": "person-name-item"})
        return [
            RezkaPerson(
                person_id=x.get("data-id"),
                name=x.find("a").text.strip(),
                url=x.find("a").get("href"),
                photo_url=x.get("data-photo"),
            )
            for x in persons
        ]


class LinkAttribute(BaseAttribute):
    @cached_property
    def value(self) -> List[RezkaLink]:
        links = self.value_tag.find_all("a")
        return [RezkaLink(url=link.get("href"), title=link.text.strip()) for link in links]


def _lazy_attr(attr_name: str, cls: Type[_T]) -> Type[_T]:
    def _lazy_object(*args, **kwargs) -> _T:
        obj = cls(*args, **kwargs)
        obj._attr_name = attr_name
        return obj

    return _lazy_object
