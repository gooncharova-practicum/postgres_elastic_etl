"""Основной файл для загрузки данных из sqlite в PotgreSQL""" 

import os
import sqlite3
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from config import dsl
from postgres_saver import PostgresSaver
from sqlite_reader import SQLiteExtractor
from utils import db_tables


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection) -> None:
    """Основной метод загрузки данных из SQLite в Postgres"""
    sqlite_reader = SQLiteExtractor(connection)
    pg_saver = PostgresSaver(pg_conn)

    for model, db_table in db_tables.items():
        data = sqlite_reader.get_data(db_table)
        pg_saver.save_data(model, data, db_table)


if __name__ == '__main__':
    db_path = os.environ.get('DB_PATH', 'db.sqlite')
    with (conn_context(db_path) as sqlite_conn,
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn):
        load_from_sqlite(sqlite_conn, pg_conn)
