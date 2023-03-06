"""Класс для загрузки подготовленных в эластик"""

from logging import getLogger

from elasticsearch import helpers, Elasticsearch
from config import index_name, index_settings
from state import State


class ElasticLoader:
    def __init__(self, elastic_obj: Elasticsearch, data: list) -> None:
        self.elastic_obj = elastic_obj
        self.data = data
        self.logger = getLogger()
    
    def load_data(self):
        """Загрузить данные пачкой"""
        helpers.bulk(self.elastic_obj, self.data)

    def create_index(self) -> bool: 
        """Создать индекс""" 
        try:
            if not self.elastic_obj.indices.exists(index_name):
                self.elastic_obj.indices.create(index=index_name, body=index_settings) 
                return True 
        except Exception as ex:
            self.logger.critical(ex) 
