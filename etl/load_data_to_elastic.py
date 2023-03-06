"""Основной файл для загрузки данных из PotgreSQL в ElasticSearch""" 

import time
from contextlib import closing

import backoff
import psycopg2
import requests
from elasticsearch import Elasticsearch
from psycopg2.extras import DictCursor
from redis import Redis

from config import PostgresSettings, es_url, redis_dsl, sleep_time
from data_transformer import DataTransformer
from elastic_loader import ElasticLoader
from postgres_extractor import PostgresExtractor
from state import RedisStorage, State


@backoff.on_exception(backoff.expo, 
                      (requests.exceptions.Timeout,
                      requests.exceptions.ConnectionError,
                      requests.exceptions.RequestException,
                      psycopg2.OperationalError))
def load_from_postgres(elastic_obj: Elasticsearch, curs: DictCursor, state: State):
    """Основной метод загрузки данных из PostgreSQL в ElasticSearch"""
    while True:
        #extract
        pg_extractor = PostgresExtractor(curs)
        data, new_states_dict = pg_extractor.extract_data(state)
        if not data:
            return

        #transform
        data_transformer = DataTransformer(data)
        transform_data = data_transformer.transform_data()

        #load
        elastic_loader = ElasticLoader(elastic_obj, transform_data)
        elastic_loader.create_index()
        elastic_loader.load_data()

        # set new states
        for redis_key, new_state in new_states_dict.items():
            state.set_state(redis_key, new_state)


if __name__ == '__main__':
    redis_adapter = Redis(host=redis_dsl['host'], port=redis_dsl['port'], db=redis_dsl['db'])
    redis_storage = RedisStorage(redis_adapter)
    state = State(redis_storage)

    while True:
        elastic_obj = Elasticsearch(es_url)
        with closing(psycopg2.connect(**PostgresSettings().dict(), 
                                      cursor_factory=DictCursor)) as pg_conn, pg_conn.cursor() as curs:
            load_from_postgres(elastic_obj, curs, state)
        elastic_obj.close()
        time.sleep(sleep_time)
