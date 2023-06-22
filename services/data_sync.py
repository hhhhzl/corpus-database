# -------------------------------------------------------------------------------------------------
#  与训练路径进行同步，获取最新的训练路径/文件/图片，并与数据库同步。
#  每周周末执行一次。
#  监控训练路径的改变情况
# -------------------------------------------------------------------------------------------------

from collections import Counter
import statistics
from flask import jsonify
from configs.mysql_config import get_db_session_sql
from blueprints.dataApi.models import (
    FileInfo,
    PathInfo,
    PageImagesInfo,
    Contents
)
from pprint import pprint
import os
from utils import abspath
from utils.logger_tools import get_general_logger
import logging
from datetime import datetime
from PIL import Image
import mysql.connector
import pandas as pd
from utils.structure import TreeNode


class DataModelStruct:
    @staticmethod
    def path_model(
            path: str,
            depth: int,
            label: int) -> tuple:
        return path, depth, label

    @staticmethod
    def file_model(
            file_name: str,
            father_label: int
    ) -> tuple:
        return file_name, father_label

    @staticmethod
    def page_image_model(
            page_name: str,
            page_inner_id: int,
            image_url: str,
            height: int,
            width: int,
            redis_key_value: str) -> tuple:
        struct = (page_name, page_inner_id, image_url, height, width, redis_key_value)
        return struct

    @staticmethod
    def content_model(
            name: str,
            content_type: str,
            content: str,
            content_location: str,
            redis_key_value: str) -> tuple:
        struct = (name, content_type, content, content_location, redis_key_value, 1, True)
        return struct


class DataProcess:
    def __init__(self, root_path, label):
        self.root_path = root_path
        self.root_symbol = 'root'
        self.label = label
        self.ignore_paths = [
            '.idea',
            '.DS_Store',
            '__pycache__',
            '.ipynb_checkpoints'
        ]

        # 构建数据struct
        self.database_dataframe = {
            'Files': [],
            'Paths': [],
            'PageImages': [],
            'Contents': []
        }
        self.label_path = {self.label: self.root_path}
        self.path_count = {self.root_path: self.label}  # full path
        self.path_tree = {self.label: self.root_symbol}  # "path": "father (self_id, father_id)"
        self.path_depth = {self.label: 1}
        self.file_page = {}

    def process_paths(self, folder_path):
        self.label += 1

        for root, dirs, files in os.walk(folder_path):
            if root in self.path_count:
                for d_item in dirs:
                    if d_item not in self.ignore_paths:
                        father_label = self.path_count[root]
                        if self.path_depth[father_label] < 3:
                            self.path_count[os.path.join(root, d_item)] = self.label
                            self.label_path[self.label] = d_item
                            self.path_tree[self.label] = father_label
                            self.path_depth[self.label] = self.path_depth[father_label] + 1

                            item_struct = DataModelStruct.path_model(d_item, self.path_depth[father_label] + 1,
                                                                     self.label)
                            self.database_dataframe['Paths'].append(item_struct)
                            self.label += 1
                        elif self.path_depth[father_label] == 3:
                            if d_item[:-4] not in self.file_page:
                                self.file_page[d_item[:-4]] = 1
                                item_struct = DataModelStruct.file_model(
                                    file_name=d_item[:-4],
                                    father_label=father_label
                                )
                                self.database_dataframe['Files'].append(item_struct)

            for f_item in files:
                unique_id = 1
                if f_item not in self.ignore_paths:
                    self.process_contents(f_item, unique_id, root)

    def process_images(self, f_item, unique_id, item_path):
        page = f_item[17:18]
        image = Image.open(item_path)
        width, height = image.size
        item_struct = DataModelStruct.page_image_model(
            page_name=f"{f_item}",
            redis_key_value=f'{f_item}:{page}:{unique_id}',
            image_url=item_path,
            page_inner_id=int(f_item[17:18]),
            width=width,
            height=height
        )
        self.database_dataframe['PageImages'].append(item_struct)

    # Tips：在搜索txt的时候，就把坐标导出来
    def process_contents(self, f_item, unique_id, root):
        item_struct = None
        item_path = os.path.join(root, f_item)
        if f_item.endswith(".xlsx") or f_item.endswith(".xlx"):
            _content = pd.read_excel(item_path, index_col=False).to_json(orient="values")
            page = f_item[17:18]  # Update page value based on the parent folder name
            item_struct = DataModelStruct.content_model(
                name=f_item,
                content_type='table',
                content=_content,
                content_location="NULL",
                redis_key_value=''
            )
            self.database_dataframe['Contents'].append(item_struct)
        elif f_item.startswith("A020") and f_item.endswith(".txt"):
            page = f_item[17:18]
            item_struct = DataModelStruct.content_model(
                name=f_item,
                content_type='text',
                content="'" + str(open(item_path, 'r', encoding='utf-8').read()) + "'",
                content_location="'" + self.process_locations(f_item) + "'",
                redis_key_value=''
            )
            self.database_dataframe['Contents'].append(item_struct)
        elif f_item.startswith("A020") and (f_item.endswith(".jpg") or f_item.endswith(".png")):
            self.process_images(f_item, unique_id, item_path)
            unique_id += 1

    def process_locations(self, f_item):
        processing_list_folder = os.path.join(self.root_path, "processing_list")
        search_folder_name = f_item[:4]

        for root, dirs, files in os.walk(processing_list_folder):
            for dir_name in dirs:
                if dir_name.startswith(search_folder_name) and dir_name.endswith("labels"):
                    labels_folder_path = os.path.join(root, dir_name)
                    file_name = f_item[:18] + '.txt'
                    txt_file_path = os.path.join(labels_folder_path, file_name)
                    if os.path.isfile(txt_file_path):
                        with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
                            text_content = txt_file.read()
                            return text_content
        return "NULL"


class DataSync(DataProcess):
    def run_update_sync(self, folder_path=None):
        if self.root_path and not folder_path:
            folder_path = self.root_path
        root_data = DataModelStruct.path_model(folder_path, 1, self.label)
        self.database_dataframe['Paths'].append(root_data)
        self.process_paths(folder_path)


if __name__ == "__main__":
    engine = DataSync('/Users/zhilinhe/desktop/ocr', 0)
    engine.run_update_sync()
    pprint(engine.database_dataframe)
    # pprint(engine.path_tree)
