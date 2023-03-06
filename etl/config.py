import datetime
import os

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()


class PostgresSettings(BaseSettings):
    dbname: str = Field(..., env='DB_NAME')
    user: str = Field(..., env='DB_USER')
    password: str = Field(..., env='DB_PASSWORD')
    host: str = Field(..., env='DB_HOST')
    port: str = Field(..., env='DB_PORT')
    options: str = '-c search_path=content'

es_url = f"http://{os.environ.get('ELASTIC_HOST', '127.0.0.1')}:{os.environ.get('ELASTIC_PORT', 9200)}"

redis_dsl = {
    'host': os.environ.get('REDIS_HOST', '127.0.0.1'), 
    'port': os.environ.get('REDIS_PORT', 6379),
    'db': os.environ.get('REDIS_DB', 0)
    }

# при отсутствии последнего стейта (чаще всего при первом запуске) берем этот дейттайм
default_modified_date = datetime.datetime(1900, 1, 1, 0, 0, 0)

# время ожидания
sleep_time = 100

# ключи для сохранения стейтов из разных таблиц
redis_keys = {'film_work': 'film_work_modified', 'genre': 'genre_modified', 'person': 'person_modified'}

postgres_scheme_name = 'content'

# имя индекса 
index_name = 'movies' 

# схема индекса 
index_settings = { 
    "settings": { 
        "refresh_interval": "1s", 
        "analysis": { 
            "filter": { 
                "english_stop": { 
                    "type": "stop", 
                    "stopwords": "_english_" 
                }, 
                "english_stemmer": { 
                    "type": "stemmer", 
                    "language": "english" 
                }, 
                "english_possessive_stemmer": { 
                    "type": "stemmer", 
                    "language": "possessive_english" 
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "imdb_rating": {
                "type": "float"
            },
            "genre": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {
                    "raw": {
                        "type": "keyword"
                    }
                }
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "director": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "actors_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "writers_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "actors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "person_id": {
                        "type": "keyword"
                    },
                    "person_name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "writers": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "person_id": {
                        "type": "keyword"
                    },
                    "person_name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            }
        }
    }
}
