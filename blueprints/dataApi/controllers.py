from collections import Counter
import datetime
import statistics
from flask import jsonify
import pandas as pd
from configs.mysql_config import get_db_session_sql
from blueprints.dataApi.models import CorpusDatabase, CorpusSubjects
from sqlalchemy import null, select, union_all, and_, or_, join, outerjoin, update, insert, delete
from pprint import pprint
import simplejson as json
import os
from utils import abspath, generate_random_color
from utils.logger_tools import get_general_logger
import logging
import pandas
from blueprints.dataApi.serializer import Serializer as s
from utils.NeuraGraphAPIs.HugeGraphAPIs import hugegraphClient
from configs.graphs_config import GRAPH_DATABASE

logger = get_general_logger('dataApi', path=abspath('logs', 'dataApi'))

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
                data.dropna(inplace=True)
                # data.drop_duplicates(subset=['noun'], inplace=True)
                s_l = []
                for id, row in data.iterrows():
                    # if not pd.isnull(row['trans']) and not pd.isnull(row['word']):
                    word = dict(
                        noun=row['noun'],
                        eng_name=row['eng_name'],
                        create_time=datetime.datetime.now(),
                        last_update_time=datetime.datetime.now(),
                    )
                    # word = CorpusDatabase(
                    #
                    # )
                    s_l.append(word)
                    # session.add(word)

                #
                session.execute(
                    insert(CorpusDatabase),
                    s_l
                )

                try:
                    session.commit()
                    logger.info(f"Words data saved.")

                except Exception as e:
                    logger.info(f'{e}')
                    session.rollback()

                    raise e

        except Exception as e:
            logging.info(f"No Words data to migrate. {str(e)}")

        try:
            with get_db_session_sql('corpus') as session:
                data = pd.read_csv(path + "/init_subjects.csv")
                data.dropna(inplace=True)
                s_l = []
                for id, row in data.iterrows():
                    word = dict(
                        id=row['subject_id'],
                        subject_name=row['subject_name'],
                        subject_chinese=row['subject_chinese'],
                        subject_abb=row['subject_abbre'],
                        father_subject=row['father_id'],
                        create_time=datetime.datetime.now(),
                        last_update_time=datetime.datetime.now(),
                    )
                    s_l.append(word)
                    # word = CorpusSubjects(
                    #     id=row['id'],
                    #     subject_name=row['subjects'],
                    #     subject_chinese=row['subjects_c'],
                    #     father_subject=row['father_id'],
                    #     create_time=datetime.datetime.now(),
                    #     last_update_time=datetime.datetime.now(),
                    # )
                    # session.add(word)

                session.execute(
                    insert(CorpusSubjects),
                    s_l
                )

                try:
                    session.commit()
                    logger.info(f"Subjects data saved.")
                except Exception as e:
                    session.rollback()
                    logger.info(f"{e}")
                    raise e
        except Exception as e:
            logger.info(f"No subjects data to migrate. {str(e)}")

    @staticmethod
    def data_import(data_file=None):
        if data_file:
            path = abspath('static', 'init')
            try:
                with get_db_session_sql('corpus') as session:
                    data = pd.read_csv(path + data_file)

                    s_l = []
                    for id, row in data.iterrows():
                        # if not pd.isnull(row['trans']) and not pd.isnull(row['word']):
                        word = dict(
                            noun=row['noun'],
                            eng_name=row['eng_name'],
                            create_time=datetime.datetime.now(),
                            last_update_time=datetime.datetime.now(),
                        )
                        s_l.append(word)

                    session.execute(
                        insert(CorpusDatabase),
                        s_l
                    )

                    try:
                        session.commit()
                        logger.info(f"Words data saved.")

                    except Exception as e:
                        logger.info(f'{e}')
                        session.rollback()
                        raise e

            except:
                logger.info(f"No Words data to migrate.")

    @staticmethod
    def fetch_corpus_data(page=None, location=None):
        record_per_page = 200
        if not page and not location:
            location = 0
        if not location and page:
            location = (page - 1) * record_per_page

        with get_db_session_sql('corpus') as session:
            records = (
                session.query(CorpusDatabase)
                .limit(record_per_page)
                .offset(location)
                .all()
            )
            data = s.serialize_list(records)
        return data

    @staticmethod
    def fetch_subject_data(page=None, location=None):
        record_per_page = 200
        if not page and not location:
            location = 0
        if not location and page:
            location = (page - 1) * record_per_page

        with get_db_session_sql('corpus') as session:
            records = (
                session.query(CorpusSubjects)
                .limit(record_per_page)
                .offset(location)
                .all()
            )
            data = s.serialize_list(records)
        return data

    @staticmethod
    def fetch_relationship_graphs(group, property_name, keyword, number_to_show=50, depth=2):
        graph_db = GRAPH_DATABASE['hugegraph']
        hg = hugegraphClient.HugeGraphClient(
            host=f"{graph_db['HOST']}",
            port=f"{graph_db['PORT']}",
            graph_name=f"{graph_db['GRAPH_NAME']}"
        )
        try:
            depth_text = f".bothE().limit({number_to_show}).otherV()"
            s = ""
            for i in range(depth):
                s += depth_text

            request = {
                "gremlin": f"g.traversal().V().hasLabel('{group}').has('{property_name}','{keyword}'){s}.path()",
                "bindings": {},
                "language": "gremlin-groovy",
                "aliases": {
                    "g": "STCKG"}
            }
            res_p = json.loads(hg.execute_germlin_post(
                gremlin=request['gremlin'],
                aliases=request['aliases']
            ).response)

            vertex_ids, edge_ids = {}, {}
            vertices, edges = [], []
            v_labels, e_labels = {}, {}
            colors, vertices_usage = {}, {}
            count = 1
            if res_p['status']['code'] == 200:
                data = res_p['result']['data']
                if data == []:
                    return False, "未找到对应的关键词"
                for each in data:
                    info = each['objects']
                    for item in info:
                        if item['type'] == 'vertex':
                            if item['label'] not in v_labels:
                                v_labels[item['label']] = 1
                                colors[item['label']] = generate_random_color()

                            if item['id'] not in vertex_ids:
                                vertex_ids[item['id']] = len(list(vertex_ids.keys())) + 1

                            if item['id'] not in vertices_usage:
                                vertices_usage[item['id']] = 1
                                dic = dict(
                                    id=vertex_ids[item['id']],
                                    group=item['label'],
                                    color=colors[item['label']],
                                    properties=item["properties"],
                                )
                                vertices.append(dic)

                        elif item['type'] == 'edge':
                            if item['label'] not in e_labels:
                                e_labels[item['label']] = 1
                                colors[item['label']] = generate_random_color()

                            if item['outVLabel'] not in v_labels:
                                v_labels[item['outVLabel']] = 1
                                colors[item['outVLabel']] = generate_random_color()

                            if item['inVLabel'] not in v_labels:
                                v_labels[item['inVLabel']] = 1
                                colors[item['inVLabel']] = generate_random_color()

                            if item['id'] not in edge_ids:
                                edge_ids[item['id']] = len(list(edge_ids.keys())) + 1

                            if item['inV'] not in vertex_ids:
                                vertex_ids[item['inV']] = len(list(vertex_ids.keys())) + 1

                            if item['outV'] not in vertex_ids:
                                vertex_ids[item['outV']] = len(list(vertex_ids.keys())) + 1

                            dic = {
                                'id': count,
                                'from': vertex_ids[item['outV']],
                                'color': colors[item['label']],
                                'to': vertex_ids[item['inV']],
                                'toGroup': item['inVLabel'],
                                'fromGroup': item['outVLabel'],
                                'properties': item["properties"],
                                'group': item['label'],
                            }
                            edges.append(dic)
                            count += 1

                for key in v_labels.keys():
                    v_labels[key] = colors[key]
                for key in e_labels.keys():
                    e_labels[key] = colors[key]

                response = {
                    "nodes": vertices,
                    "edges": edges,
                    "nodes_l": v_labels,
                    "edges_l": e_labels,
                }
                return True, response
            else:
                logger.info(f"Fetch Failed: Response Error (not 200)")
                return False, "Fetch Failed: Response Error (not 200)"

        except Exception as e:
            logger.info(f"Fetch Failed: {str(e)}")
            return False, f"Fetch Failed: {str(e)}"


if __name__ == '__main__':
    # Control = DataController()
    # print(Control.fetch_subject_data(page=1))
    path = abspath('static', 'init')
    data = pd.read_csv(path + "/init_words.csv")
    data.dropna(inplace=True)
    # data.drop_duplicates(subset=['noun'], inplace=True)
    print(data.shape[0])
