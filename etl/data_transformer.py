"""Класс подготовки данных для загрузки в эластик"""

import json
from logging import getLogger

from config import index_name


class DataTransformer:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.logger = getLogger()
    
    def transform_data(self):
        """Преобразование данных в необходимый для загрузки формат"""

        try:
            transform_data = [
                {
                    "_index": index_name,
                    "_id": doc["id"],
                    "_source": json.dumps({key: value for key, value in doc.items()})
                } 
                for doc in self.data
            ]
            self.logger.debug('Data tranformed succesfully')
            return transform_data

        except Exception as e:
            self.logger.error(f'Data transformed with error: {e}')
