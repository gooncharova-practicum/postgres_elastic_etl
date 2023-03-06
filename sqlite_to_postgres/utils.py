from dataclass_models import (
    DataClassFilmWork,
    DataClassGenre,
    DataClassGenreFilmwork,
    DataClassPerson,
    DataClassPersonFilmwork
    )

db_tables = {
    DataClassFilmWork: 'film_work',
    DataClassGenre: 'genre',
    DataClassPerson: 'person',
    DataClassGenreFilmwork: 'genre_film_work',
    DataClassPersonFilmwork: 'person_film_work'
}


def get_right_dict_keys(data):
    try:
        data['created'] = data.pop('created_at')
    except KeyError:
        pass
    try:
        data['modified'] = data.pop('updated_at')
    except KeyError:
        pass
    return data
