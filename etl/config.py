import os

from dotenv import load_dotenv
import datetime

load_dotenv()


dsl = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port':  os.environ.get('DB_PORT', 5432),
    }

es_url = f"http://{os.environ.get('ELASTIC_HOST', '127.0.0.1')}:{os.environ.get('ELASTIC_PORT', 9200)}"

redis_dsl = {
    'host': os.environ.get('REDIS_HOST', '127.0.0.1'), 
    'port': os.environ.get('REDIS_PORT', 6379),
    'db': os.environ.get('REDIS_DB', 0)
    }

default_modified_date = datetime.datetime(1900, 1, 1, 0, 0, 0)

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
