"""Основной файл для загрузки данных из PotgreSQL в ElasticSearch""" 

import time

import backoff
import psycopg2
import requests
from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from redis import Redis

from config import default_modified_date, dsl, es_url, redis_dsl
from data_transformer import DataTransformer
from elastic_loader import ElasticLoader
from postgres_extractor import PostgresExtractor
from state import RedisStorage, State


@backoff.on_exception(backoff.expo, 
                      (requests.exceptions.Timeout,
                      requests.exceptions.ConnectionError,
                      requests.exceptions.RequestException,
                      psycopg2.OperationalError))
def load_from_postgres(elastic_obj: Elasticsearch, pg_conn: _connection, state: State):
    """Основной метод загрузки данных из PostgreSQL в ElasticSearch"""
    while True:
        #extract
        pg_extractor = PostgresExtractor(pg_conn)
        old_state = state.get_state('modified')
        if not old_state:
            old_state = default_modified_date
        data, new_state = pg_extractor.extract_data(old_state)
        if not data:
            return

        #transform
        data_transformer = DataTransformer(data)
        transform_data = data_transformer.transform_data()

        #load
        elastic_loader = ElasticLoader(elastic_obj, transform_data)
        elastic_loader.create_index()
        elastic_loader.load_data()
        state.set_state('modified', new_state)


if __name__ == '__main__':
    elastic_obj = Elasticsearch(es_url)
    redis_adapter = Redis(host=redis_dsl['host'], port=redis_dsl['port'], db=redis_dsl['db'])
    redis_storage = RedisStorage(redis_adapter)
    state = State(redis_storage)

    while True:
        with psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
            load_from_postgres(elastic_obj, pg_conn, state)
        pg_conn.close()
        time.sleep(100)
