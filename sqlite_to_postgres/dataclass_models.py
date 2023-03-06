import datetime
import uuid
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class DataClassTimeStampedMixin:
    created: datetime.datetime
    modified: datetime.datetime


@dataclass
class DataClassFilmWork(DataClassTimeStampedMixin):
    creation_date: datetime.date
    title: str
    type: Literal['tv_show', 'movie']
    description: str = field(default='')
    file_path: str = field(default='')
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class DataClassGenre(DataClassTimeStampedMixin):
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    description: str = field(default='')


@dataclass
class DataClassPerson(DataClassTimeStampedMixin):
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class DataClassGenreFilmwork:
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class DataClassPersonFilmwork:
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    created: datetime.datetime
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
