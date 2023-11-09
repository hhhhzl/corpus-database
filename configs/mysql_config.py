from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

MYSQL_SETTINGS = {
    "corpus": {
        "HOST": "localhost",
        "PORT": 3306,
        "USERNAME": "root",
        "PASSWORD": "Mysql-60003",
        "DB": "Corpus_STA_DB",
        "CONNECTOR": "pymysql"
    }
}


def get_db_uri(CONNECTOR, USERNAME, PASSWORD, HOST, PORT, DB):
    return f'mysql+{CONNECTOR}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'


def get_db_session_sql(db) -> Session:
    return sessionmaker(ENGINES[db], autocommit=True)()


DB_URI_CORPUS = get_db_uri(**MYSQL_SETTINGS["corpus"])

ENGINES = {
    "corpus": create_engine(DB_URI_CORPUS,
                            max_overflow=-1,
                            pool_pre_ping=True,
                            pool_recycle=3600)
}

BASES = {
    "corpus": declarative_base(ENGINES["corpus"])
}