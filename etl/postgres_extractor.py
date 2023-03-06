"""Основной файл для загрузки данных из PostgreSQL в ElasticSearch""" 

from logging import getLogger
from typing import Any, Tuple

from psycopg2.extras import DictCursor

from config import default_modified_date, redis_keys, postgres_scheme_name
from state import State


class PostgresExtractor:
    LIMIT = 100 # количество id фильмов, получаемых за один запрос
    SIZE = 100 # количество записей, получаемых за один запрос в extract_data
    SCHEME = postgres_scheme_name

    def __init__(self, curs: DictCursor) -> None:
        self.cursor = curs
        self.logger = getLogger()

    def extract_data(self, state: State) -> Tuple[dict, dict]:
        new_states = {}
        all_ids = {}
        for table_name, redis_key in redis_keys.items():
            old_state = state.get_state(redis_key)
            if not old_state:
                old_state = default_modified_date
            ids, new_state = self.get_ids_and_modified_from_table(table_name, old_state)
            all_ids[table_name] = ids if ids else '(NULL)'
            new_states[redis_key] = new_state
        
        film_work_ids = self.get_film_works_ids(all_ids['film_work'], all_ids['genre'], all_ids['person'])
        self.logger.debug(f'Extracted {len(film_work_ids)} film_works_ids')

        if film_work_ids:
            self.cursor.execute(self._get_query(film_work_ids))
            return self.cursor.fetchmany(size=self.SIZE), new_states
        return {}, new_states

    def get_ids_and_modified_from_table(self, table_name: str, state: Any) -> Tuple[tuple, Any]:
        query = f"""SELECT 
                    id, 
                    to_char(modified, 'YYYY-MM-DD HH24:MI:SS.US') as modified
                FROM {self.SCHEME}.{table_name} 
                WHERE modified > '{state}'
                ORDER BY modified
                LIMIT {self.LIMIT}"""
        self.cursor.execute(query)
        ids = self.cursor.fetchmany(size=self.SIZE)
        if ids:
            return tuple([item.get('id') for item in ids]) if len(ids) > 1 else f"('{ids[0]}')", ids[-1].get('modified')
        return tuple(), state
    
    def get_film_works_ids(self, film_works_ids, genre_ids, person_ids) -> tuple:
        """Получаем пачку фильмов для загрузки"""

        if film_works_ids == genre_ids == person_ids == '(NULL)':
            return tuple()

        self.cursor.execute( 
            f"""SELECT DISTINCT
                    fw.id
                FROM {self.SCHEME}.film_work fw 
                LEFT JOIN {self.SCHEME}.genre_film_work gfw 
                ON fw.id = gfw.film_work_id 
                LEFT JOIN {self.SCHEME}.person_film_work pfw 
                ON fw.id = pfw.film_work_id 
                WHERE gfw.genre_id IN {genre_ids}
                OR pfw.person_id IN {person_ids}
                OR fw.id IN {film_works_ids}
                LIMIT {self.LIMIT};""")
        
        film_works = self.cursor.fetchmany(size=self.SIZE)
        return tuple([item.get('id') for item in film_works]) if film_works else tuple()

    def _get_query(self, films_work_ids: tuple) -> str:
        """Формируем sql-запрос"""

        return f"""SELECT COALESCE (
            json_agg(
                DISTINCT jsonb_build_object(
                    'person_id', p.id,
                    'person_name', p.full_name)
                    )
                    FILTER (WHERE p.id is not null and pfw.role = 'actor'), '[]') as actors,
                        array_remove(array_agg(DISTINCT p.full_name)
                    FILTER (WHERE pfw.role = 'actor'), null) as actors_names,
               fw.description,
               array_remove(array_agg(DISTINCT p.full_name)
                    FILTER (WHERE pfw.role = 'director'), null) as director,
               array_agg(DISTINCT g.name) as genre,
               fw.id,
               fw.rating as imdb_rating,
               fw.title,
               COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'person_id', p.id,
                           'person_name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null and pfw.role = 'writer'),
                   '[]'
               ) as writers,
               array_remove(array_agg(DISTINCT p.full_name)
                    FILTER (WHERE pfw.role = 'writer'), null) as writers_names
            FROM {self.SCHEME}.film_work fw
            LEFT JOIN {self.SCHEME}.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN {self.SCHEME}.person p ON p.id = pfw.person_id
            LEFT JOIN {self.SCHEME}.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN {self.SCHEME}.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN {films_work_ids}
            GROUP BY fw.id
            ORDER BY fw.modified"""
