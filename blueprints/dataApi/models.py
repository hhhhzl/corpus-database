from email.policy import default
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric
from sqlalchemy import inspect, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from configs.postgres_config import ENGINES, BASES, get_db_session


class FileInfo(BASES['corpus']):
    __tablename__ = "FileInfo"
    __table_args__ = (
        UniqueConstraint('uuid_id', 'filename'),
    )

    id = Column(Integer, primary_key=True)
    uuid_id = Column(String(100))
    filename = Column(String(100))
    filepath = Column(String(100), default="/static/upload")

    def __str__(self) -> str:
        s = f'(U: {self.uuid_id} N: {self.filename} P: {self.filepath}'
        return s

    def __repr__(self) -> str:
        s = f'(U: {self.uuid_id} N: {self.filename} P: {self.filepath}'
        return s


class CorpusDatabase(BASES['corpus']):
    __tablename__ = "CorpusDatabase"

    id = Column(Integer, autoincrement=True, primary_key=True)
    noun = Column(String(100))
    eng_name = Column(String(100))
    abb = Column(String(20))
    subject = Column(String(20))
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb} s: {self.subject}'
        return s

    def __repr__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb} s: {self.subject}'
        return s


class CorpusHistory(BASES['corpus']):
    __tablename__ = "CorpusHistory"

    id = Column(Integer, autoincrement=True, primary_key=True)
    noun = Column(String(100))
    eng_name = Column(String(100))
    abb = Column(String(20))
    subject = Column(String(20))
    create_time = Column(DateTime)
    category = Column(String(1))

    def __str__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb} s: {self.subject} t: {self.create_time} c: {self.category}'
        return s

    def __repr__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb} s: {self.subject} t: {self.create_time} c: {self.category}'
        return s


if __name__ == "__main__":
    for BASE in BASES.values():
        BASE.metadata.create_all()
