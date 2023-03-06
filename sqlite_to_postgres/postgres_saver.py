from dataclasses import astuple
from logging import getLogger

import psycopg2

from utils import get_right_dict_keys


class PostgresSaver:
    SCHEMA = 'content'

    def __init__(self, connection) -> None:
        self.connection = connection
        self.cursor = connection.cursor()
        self.logger = getLogger()

    def save_data(self, model, data, db_table):
        count_sqlite_rows = 0
        count_inserted_rows = 0

        for raw_row in data:
            count_inserted_rows += 1
            raw_dict_row = dict(raw_row)
            row = get_right_dict_keys(raw_dict_row)
            query = self.__get_query(db_table, model, 'id')
            values_for_insert = self.get_values_for_insert(model, row)
            try:
                psycopg2.extras.execute_batch(self.cursor,
                                              query,
                                              (values_for_insert, ))
                rowcount = self.cursor.rowcount
                self.connection.commit()
                count_sqlite_rows += rowcount

            except psycopg2.errors.UniqueViolation as unique_error:
                # можно 2 ошибки одновременно обработать
                # это задел на будущее для более четких инструкций в ON CONFLICT)
                self.logger.error(f'{unique_error} in row {raw_dict_row}')

            except psycopg2.IntegrityError as error:
                self.logger.error(f'{error} in row {raw_dict_row}')

        self.logger.debug(f'Data insertion complited. Inserted {count_inserted_rows} rows from {count_sqlite_rows}')

    def get_values_for_insert(self, model, row):
        return astuple(model(**row))

    @staticmethod
    def get_columns(fields):
        return ', '.join(field for field in fields)

    @staticmethod
    def get_values_amount(fields):
        values = ''
        for _ in range(len(fields)):
            values += '%s, '
        return values[:-2]

    def __get_query(self, db_table, model, unique_column):
        fields = model.__dataclass_fields__.keys()
        columns = self.get_columns(fields)
        values = self.get_values_amount(fields)
        return (f"INSERT INTO {self.SCHEMA}.{db_table} ({columns}) VALUES ({values}) ON CONFLICT ({unique_column}) DO NOTHING;")
