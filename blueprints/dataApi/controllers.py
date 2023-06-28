from collections import Counter
import datetime
import pandas as pd
from configs.mysql_config import get_db_session_sql
from blueprints.dataApi.models import (
    PathInfo,
    PageImagesInfo,
    Contents_backup,
    Contents,
    FileInfo
)
from pprint import pprint
from utils import abspath
from utils.logger_tools import get_general_logger
import logging
from blueprints.dataApi.serializer import Serializer as s
from utils.redis_tools import RedisWrapper
import uuid as u
import base64

logger = get_general_logger('dataApi', path=abspath('logs', 'dataApi'))
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class DataController:

    # def __init__(self, user_number):
    #     self.user_number = user_number
    def __init__(self):
        pass

    @staticmethod
    def _search_path_file(id=None):
        father_id = None
        if not id:
            father_id = -1
        else:
            father_id = id

        with get_db_session_sql('predict') as session:
            records = (
                session.query(PathInfo)
                .filter(PathInfo.father_id == father_id)
                .all()
            )
            if not records:
                files = (
                    session.query(FileInfo)
                    .filter(FileInfo.father_path == father_id)
                    .all()
                )

                not_show = ['create_time']
                return s.serialize_list(files, not_show)

            else:
                return s.serialize_list(records)

    @staticmethod
    def _search_file_page(id):
        with get_db_session_sql('predict') as session:
            records = (
                session.query(PageImagesInfo)
                .filter(PageImagesInfo.father_Path == id)
                .filter(PageImagesInfo.sub_page == 1)
                .all()
            )
            not_show = ['sub_page', 'create_time','last_update_time']
            data = s.serialize_list(records, not_show)

            # redis缓存
            redis_cli = RedisWrapper('p_image')

            for row in data:
                value = redis_cli.get(row['redis_key_value'])
                if not value:
                    with open(row['image_url'], "rb") as img_file:
                        base64_bytes = base64.b64encode(img_file.read())
                        base64_string = base64_bytes.decode('utf-8')
                    redis_cli.set(key=row['redis_key_value'], ex=60*60*6, value=base64_string)
                    row['image_url'] = base64_string
                else:
                    row['image_url'] = value
            return sorted(data, key=lambda d: d['page_inner_id'])

    @staticmethod
    def _search_content(image_id, uuid=None):
        with get_db_session_sql('predict') as session:
            records = (
                session.query(Contents)
                .filter(Contents.father_page == image_id)
                .filter(Contents.is_active == True)
                .all()
            )
            data = s.serialize_list(records, ["is_active", 'create_time', 'last_update_time'])

            # 查看lock状况
            redis_cli = RedisWrapper('p_lock')
            value = redis_cli.get(f'predict:lock:{image_id}')

            # 有锁
            if value:
                # 无uuid或uuid不匹配，无法解锁
                if not uuid  or uuid != value:
                    new = [{
                        'uuid': '',
                        'lock': True,
                        'contents':[dict(item, is_lock=True) for item in data] # 内容不可编辑状态
                    }]
                    return new

                # uuid匹配，延续解锁时长3s
                elif uuid == value:
                    new = [{
                        'uuid': value,
                        'lock': False,
                        'contents': [dict(item, is_lock=False) for item in data]  # 内容可编辑状态
                    }]
                    redis_cli.set(key=f'predict:lock:{image_id}', ex=10, value=value)
                    return new
            # 无锁
            else:
                uuid_id = u.uuid4()
                new = [{
                    'uuid':str(uuid_id),
                    'lock': False,
                    'contents': [dict(item, is_lock=False) for item in data] # 内容可编辑状态
                }]
                redis_cli.set(key=f'predict:lock:{image_id}', ex=10, value=str(uuid_id))
                return new
    @staticmethod
    def _update_content(id, content, location):
        with get_db_session_sql('predict') as session:
            record = (
                session.query(Contents)
                .filter(Contents.id == id)
                .one_or_none()
            )
            if record and record.create_time == record.last_update_time and record.source == 1:
                content_back_up = Contents_backup(
                    content_id = record.id,
                    content = record.content,
                    content_location = record.content_location,
                    create_time = record.create_time,
                    last_update_time = datetime.datetime.now()
                )
                session.add(content_back_up)

                try:
                    session.commit()
                except Exception as e:
                    session.rollback()


            records = (
                session.query(Contents)
                .filter(Contents.id == id)
                .update({
                    Contents.content: content,
                    Contents.content_location: location,
                    Contents.last_update_time: datetime.datetime.now()
                })
            )

            records = (
                session.query(Contents)
                .filter(Contents.id == id)
                .one_or_none()
            )

            file = (
                session.query(FileInfo)
                .filter(FileInfo.id == records.father_file)
                .update({
                    FileInfo.last_update_time: datetime.datetime.now()
                })
            )

            try:
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                return False



    @staticmethod
    def _add_content(row):
        with get_db_session_sql('predict') as session:
            file_record = (
                session.query(PageImagesInfo)
                .filter(PageImagesInfo.id == row['father_page'])
                .one_or_none()
            )
            if file_record:
                record = Contents(
                    name=row['name'],
                    content_type=row['content_type'],
                    father_file=file_record.father_Path,
                    father_page=row['father_page'],
                    content=row['content'],
                    content_location=row['content_location'],
                    redis_key_value='',
                    source=0,
                    is_active=True,
                    create_time=datetime.datetime.now(),
                    last_update_time=datetime.datetime.now(),
                )
                session.add(record)

                try:
                    session.commit()
                    return True
                except Exception as e:
                    session.rollback()
                    return e

    @staticmethod
    def _delete_content(id):
        with get_db_session_sql('predict') as session:
            record = (
                session.query(Contents)
                .filter(Contents.id == id)
                .one_or_none()
            )
            if record:
                session.delete(record)

                try:
                    session.commit()
                    return True
                except Exception as e:
                    session.rollback()
                    return e




if __name__ == '__main__':
    Control = DataController._search_file_page(id=2)
    pprint(Control)
