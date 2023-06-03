from collections import Counter
import datetime
import statistics
from flask import jsonify
import pandas as pd
from configs.mysql_config import get_db_session_sql
from blueprints.dataApi.models import CorpusDatabase, CorpusSubjects
from pprint import pprint
import simplejson as json
import os
from utils import abspath
from utils.logger_tools import get_general_logger
import logging
import pandas
from blueprints.dataApi.serializer import Serializer
logger = get_general_logger('dataApi', path=abspath('logs', 'dataApi'))
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class DataController:
    """
    查找流程：
    1。 如果user只有一个，查找post
    2. 如果user多个，查找redis merge

    """

    # def __init__(self, user_number):
    #     self.user_number = user_number

    @staticmethod
    def initial_database():
        path = abspath('static', 'init')
        try:
            with get_db_session_sql('corpus') as session:
                data = pd.read_csv(path + "/init_words.csv")

                for id, row in data.iterrows():
                    # if not pd.isnull(row['trans']) and not pd.isnull(row['word']):
                        word = CorpusDatabase(
                            noun=row['trans'],
                            eng_name=row['word'],
                            create_time=datetime.datetime.now(),
                            last_update_time=datetime.datetime.now(),
                        )
                        session.add(word)

                try:
                    session.commit()
                    logging.info(f"Words data saved.")
                except Exception as e:
                    logging.info(f'{e}')
                    session.rollback()
                    raise e

        except:
            logging.info(f"No Words data to migrate.")

        try:
            with get_db_session_sql('corpus') as session:
                data = pd.read_csv(path + "/init_subjects.csv")
                for id, row in data.iterrows():
                    word = CorpusSubjects(
                        subject_name=row['subjects'],
                        create_time=datetime.datetime.now(),
                        last_update_time=datetime.datetime.now(),
                    )
                    session.add(word)

                try:
                    session.commit()
                    logging.info(f"Subjects data saved.")
                except Exception as e:
                    session.rollback()
                    logging.info(f"{e}")
                    raise e

        except:
            logging.info(f"No subjects data to migrate.")

    @staticmethod
    def fetch_corpus_data(page=None, location=None):
        record_per_page = 200
        if not page and not location:
            location = 1
        if not location:
            location = (page-1) * record_per_page + 1

        with get_db_session_sql('corpus') as session:
            records = (
                session.query(CorpusDatabase)
                .limit(record_per_page)
                .offset(location)
                .all()
            )
        return records
        # return json.dumps(CorpusDatabase.serialize_list(records))


if __name__ == '__main__':
    Control = DataController()
    print(Control.fetch_corpus_data())
