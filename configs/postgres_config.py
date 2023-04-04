from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

POSTGRES_SETTINGS = {
    "corpus": {
        "HOST": "localhost",
        "PORT": 5432,
        "USERNAME": "postgres",
        "PASSWORD": "corpus-admin",
        "DB": "db",
        "CONNECTOR": "psycopg2"
    }
}


def get_db_uri(CONNECTOR, USERNAME, PASSWORD, HOST, PORT, DB):
    return f'postgresql+{CONNECTOR}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'


def get_db_session(db) -> Session:
    return sessionmaker(ENGINES[db])()


DB_URI_CORPUS = get_db_uri(**POSTGRES_SETTINGS["corpus"])

ENGINES = {
    "corpus": create_engine(DB_URI_CORPUS, max_overflow=-1)
}

BASES = {
    "corpus": declarative_base(ENGINES["corpus"])
}


