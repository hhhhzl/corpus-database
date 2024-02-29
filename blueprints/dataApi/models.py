from email.policy import default
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey, Text
from sqlalchemy import inspect, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from configs.mysql_config import ENGINES, BASES, get_db_session_sql
# from configs.postgres_config import ENGINES, BASES, get_db_session
from blueprints.dataApi.serializer import Serializer


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


class CorpusDatabase(BASES['corpus'], Serializer):
    __tablename__ = "Word_segmentation"

    id = Column(Integer, autoincrement=True, primary_key=True)
    noun = Column(String(1000), nullable=False)
    eng_name = Column(String(1000), nullable=False)
    attributes = Column(Text, nullable=True)
    abb = Column(String(200), nullable=True)
    synonyms = Column(Text, nullable=True)
    synonym = Column(Text, nullable=True)
    hypernym = Column(Text, nullable=True)
    hyponym = Column(Text, nullable=True)
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb})'
        return s

    def __repr__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb})'
        return s

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return Serializer.serialize(self)


class CorpusSubjects(BASES['corpus']):
    __tablename__ = "Subjects"

    id = Column(Integer, primary_key=True)
    subject_name = Column(Text)
    subject_chinese = Column(Text)
    subject_abb = Column(Text)
    father_subject = Column(Integer)
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(s: {self.subject_name} )'
        return s

    def __repr__(self) -> str:
        s = f'(s: {self.subject_name} )'
        return s

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
        }

    # @property
    # def serialize_many2many(self):
    #     """
    #     Return object's relations in easily serializable format.
    #     NB! Calls many2many's serialize property.
    #     """
    #     return [item.serialize for item in self.many2many]


class CorpusWordSubjects(BASES['corpus']):
    __tablename__ = "Word_Subjects"

    id = Column(Integer, autoincrement=True, primary_key=True)
    word_id = Column(Integer, ForeignKey('Word_segmentation.id', ondelete='CASCADE'), nullable=False)
    subject_id = Column(Integer, ForeignKey('Subjects.id', ondelete='CASCADE'), nullable=False)
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(s: {self.subject_id}, w: {self.word_id} )'
        return s

    def __repr__(self) -> str:
        s = f'(s: {self.subject_id}, w:{self.word_id})'
        return s


class CorpusHistory(BASES['corpus']):
    __tablename__ = "CorpusHistory"

    id = Column(Integer, autoincrement=True, primary_key=True)
    noun = Column(Text)
    eng_name = Column(Text)
    abb = Column(Text)
    subject = Column(Text)
    create_time = Column(DateTime)
    category = Column(String(1))

    def __str__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb} s: {self.subject} t: {self.create_time} c: {self.category})'
        return s

    def __repr__(self) -> str:
        s = f'(n: {self.noun} e: {self.eng_name} a: {self.abb} s: {self.subject} t: {self.create_time} c: {self.category})'
        return s


if __name__ == "__main__":
    for BASE in BASES.values():
        BASE.metadata.create_all()
