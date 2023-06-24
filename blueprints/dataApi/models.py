from email.policy import default
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy import inspect, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from configs.mysql_config import ENGINES, BASES, get_db_session_sql
# from configs.postgres_config import ENGINES, BASES, get_db_session
from blueprints.dataApi.serializer import Serializer

class PathInfo(BASES['predict']):
    __tablename__ = "Paths"
    # __table_args__ = (
    #     UniqueConstraint('abs_path',),
    # )

    id = Column(Integer, autoincrement=True, primary_key=True)
    path_name = Column(String(20))
    father_id = Column(Integer, nullable=False)
    depth = Column(Integer, nullable=False)
    abs_path = Column(String(100))
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(id: {self.id} p: {self.path_name} f: {self.father_id})'
        return s

    def __repr__(self) -> str:
        s = f'(id: {self.id} p: {self.path_name} f: {self.father_id})'
        return s


class FileInfo(BASES['predict']):
    __tablename__ = "Files"
    __table_args__ = (
        UniqueConstraint('file_name', ),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)
    file_name = Column(String(20), nullable=False)
    father_path = Column(Integer, ForeignKey('Paths.id', ondelete='CASCADE'), nullable=False)
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(f: {self.file_name} p: {self.father_path} )'
        return s

    def __repr__(self) -> str:
        s = f'(f: {self.file_name} p: {self.father_path} )'
        return s


class PageImagesInfo(BASES['predict']):
    __tablename__ = "PageImages"
    __table_args__ = (
        UniqueConstraint('image_url', 'redis_key_value',),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)
    page_name = Column(String(40), nullable=False)
    page_inner_id = Column(Integer)
    father_Path = Column(Integer, ForeignKey('Files.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String(150), nullable=True,unique=True)
    image_height = Column(Integer)
    image_width = Column(Integer)
    redis_key_value = Column(String(40), nullable=True, unique=True)
    sub_page = Column(Integer)
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(p: {self.page_name} f: {self.father_file}) id:{self.page_inner_id} i:{self.image_url} k:{self.redis_key_value} )'
        return s

    def __repr__(self) -> str:
        s = f'(p: {self.page_name} f: {self.father_file}) id:{self.page_inner_id} i:{self.image_url} k:{self.redis_key_value} )'
        return s


class Contents(BASES['predict']):
    __tablename__ = "Contents"
    __table_args__ = (
        UniqueConstraint('name',),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(40), nullable=False)
    father_page = Column(Integer, ForeignKey('PageImages.id', ondelete='CASCADE'), nullable=False)
    father_file = Column(Integer, ForeignKey('Files.id', ondelete='CASCADE'), nullable=False)
    content_type = Column(String(6), nullable=True)
    content = Column(String(3000), nullable=True)
    content_location = Column(String(150), nullable=True)
    redis_key_value = Column(String(30), nullable=True)
    source = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(n: {self.name}, p:{self.father_page}, f:{self.father_file}, type:{self.content_type}, c:{self.content}, l: {self.content_location} )'
        return s

    def __repr__(self) -> str:
        s = f'(n: {self.name}, p:{self.father_page}, f:{self.father_file}, type:{self.content_type}, c:{self.content}, l: {self.content_location} )'
        return s

class Contents_backup(BASES['predict']):
    __tablename__ = "Contents_Backup"
    __table_args__ = (
        UniqueConstraint('content_id',),
    )

    id = Column(Integer, autoincrement=True, primary_key=True)
    content_id = Column(Integer, ForeignKey('Contents.id', ondelete='CASCADE'), nullable=False)
    content = Column(String(1000), nullable=True)
    content_location = Column(String(150), nullable=True)
    create_time = Column(DateTime)
    last_update_time = Column(DateTime)
    last_backup_time = Column(DateTime)

    def __str__(self) -> str:
        s = f'(id: {self.id} c:{self.content_id})'
        return s

    def __repr__(self) -> str:
        s = f'(id: {self.id} c:{self.content_id})'
        return s

if __name__ == "__main__":
    for BASE in BASES.values():
        BASE.metadata.create_all()
