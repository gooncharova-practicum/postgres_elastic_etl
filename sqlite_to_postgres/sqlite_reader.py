import sqlite3
from logging import getLogger


class SQLiteExtractor:
    FETCHMANY_SIZE = 100

    def __init__(self, connection) -> None:
        self.cursor = connection.cursor()
        self.logger = getLogger()

    def get_data(self, db_table):
        query = f'SELECT * FROM {db_table};'
        count = 0

        try:
            self.cursor.execute(query)
            while data := self.cursor.fetchmany(size=self.FETCHMANY_SIZE):
                count += len(data)
                yield from data

        except sqlite3.DatabaseError as err:
            self.logger.error(err)

        self.logger.debug(f'Extract data is over. Get {count} from table {db_table}')
