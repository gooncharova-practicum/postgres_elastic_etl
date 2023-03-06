"""Основной файл для загрузки данных из PostgreSQL в ElasticSearch""" 

from logging import getLogger
from typing import Any, Tuple

from psycopg2.extensions import connection as _connection


class PostgresExtractor:
    LIMIT = 100 # количество id фильмов, получаемых за один запрос
    SIZE = 100 # количество записей, получаемых за один запрос в extract_data

    def __init__(self, connection: _connection) -> None:
        self.connection = connection
        self.cursor = connection.cursor()
        self.logger = getLogger()

    def extract_data(self, state: Any) -> Tuple[dict, Any]:
        film_works = self.get_film_works(state)
        film_work_ids = tuple()
        count_extracted_rows = 0
        for film in film_works:
            film_work_ids += tuple([film.get('id')])
            count_extracted_rows += 1
        self.logger.debug(f'Extracted {count_extracted_rows} film_works_ids')

        if film_work_ids:
            self.cursor.execute(self.__get_query(film_work_ids))
            new_state = film_works[-1].get('modified')
            return self.cursor.fetchmany(size=self.SIZE), new_state
        return {}, state
    
    def get_film_works(self, state: Any) -> dict:
        """Получаем пачку фильмов для загрузки"""

        self.cursor.execute( 
            f"""SELECT
                    id,
                    to_char(modified, 'YYYY-MM-DD HH24:MI:SS.US')
                    as modified
                FROM content.film_work
                WHERE modified > '{state}'
                ORDER BY modified
                LIMIT {self.LIMIT};""")
        return self.cursor.fetchmany(size=self.SIZE)

    def __get_query(self, films_work_ids: tuple) -> str:
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
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN {films_work_ids}
            GROUP BY fw.id
            ORDER BY fw.modified"""
