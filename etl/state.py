import abc
from typing import Any

import redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        raise NotImplementedError('Method save_state is not defined')

    @abc.abstractmethod
    def retrieve_state(self, key: str) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        raise NotImplementedError('Method retrieve_state is not defined')


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: redis.Redis) -> None:
        self.redis_adapter = redis_adapter

    def save_state(self, key: str, value: Any) -> None:
        self.redis_adapter.set(key, value)

    def retrieve_state(self, key: str) -> Any:
        return self.redis_adapter.get(key)


class State:
    """
    Класс для хранения состояния при работе с данными, 
    чтобы постоянно не перечитывать данные с начала.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state(key, value)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        state = self.storage.retrieve_state(key)
        if state:
            return state.decode('utf-8')
