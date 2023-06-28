# -------------------------------------------------------------------------------------------------
#  与训练路径进行同步，获取最新的训练路径/文件/图片，并与数据库同步。
#  每周周末执行一次。
#  监控训练路径的改变情况
# --------------- ---------------------------------------------------------------------------------

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
import datetime
from PIL import Image
import mysql.connector
import pandas as pd
from configs.environment import PREDICT_PATH as root
import re
from utils.structure import TreeNode

logger = get_general_logger('datasync', path=abspath('logs', 'data_sync'))
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


class DataModelStruct:
    @staticmethod
    def path_model(
            path: str,
            depth: int,
            abs_path:str) -> tuple:
        return path, depth, abs_path

    @staticmethod
    def file_model(
            file_name: str,
            abs_path: str
    ) -> tuple:
        return file_name, abs_path

    @staticmethod
    def page_image_model(
            page_name: str,
            page_inner_id: int,
            image_url: str,
            height: int,
            width: int,
            sub_image:int,
            file_name:str,
            redis_key_value: str) -> tuple:
        struct = (page_name, page_inner_id, image_url, height, width, redis_key_value, file_name, sub_image)
        return struct

    @staticmethod
    def content_model(
            name: str,
            content_type: str,
            content: str,
            content_location: str,
            file_name:str,
            page_inner:int,
            redis_key_value: str) -> tuple:
        struct = (name, content_type, content, content_location, redis_key_value, 1, True, file_name, page_inner)
        return struct


class DataProcess:
    def __init__(self, root_path):
        self.root_path = root_path
        self.root_symbol = ''
        self.root_name = root_path.rsplit(os.sep)[-1]
        self.read_line_count = {}  # 跟踪每个文件的已读取行数
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

        self.path_tree = {self.root_path: self.root_symbol}
        self.path_depth = {self.root_path: 1}
        self.file_page = {}
        self.sub_page = {}

    def process_paths(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            if root in self.path_tree:
                # print(root)
                for d_item in dirs:
                    if d_item not in self.ignore_paths:
                        if self.path_depth[root] < 3:

                            self.path_tree[os.path.join(root, d_item)] = root

                            self.path_depth[os.path.join(root, d_item)] = self.path_depth[root] + 1
                            item_struct = DataModelStruct.path_model(d_item, self.path_depth[root] + 1, root)
                            self.database_dataframe['Paths'].append(item_struct)
                            # print(item_struct)
                        elif self.path_depth[root] == 3:
                            if d_item[:-4] not in self.file_page:
                                self.file_page[d_item[:-4]] = 1
                                item_struct = DataModelStruct.file_model(
                                    file_name=d_item[:-4],
                                    abs_path = root
                                )
                                self.database_dataframe['Files'].append(item_struct)

            for f_item in files:
                # print(f_item)
                if f_item not in self.ignore_paths:
                    self.process_contents(f_item, root)

    def process_images(self, f_item, item_path, whether_sub):
        file_name = item_path.split('.')[0].split(os.sep)[-1][:14]
        page_name = item_path.split('.')[0].split(os.sep)[-1][:18]
        page = f_item[17:18]
        redis_key = None
        if not whether_sub:
            if page_name not in self.sub_page:
                self.sub_page[page_name] = 1
            else:
                self.sub_page[page_name] += 1
            redis_key = f'{f_item}:{page}:{whether_sub}:{self.sub_page[page_name]}'
        else:
            redis_key = f'{f_item}:{page}:{whether_sub}'

        image = Image.open(item_path)
        width, height = image.size
        item_struct = DataModelStruct.page_image_model(
            page_name=page_name,
            redis_key_value=redis_key,
            image_url=item_path,
            page_inner_id=int(f_item[17:18]),
            width=width,
            height=height,
            file_name=file_name,
            sub_image=whether_sub
        )
        self.database_dataframe['PageImages'].append(item_struct)

    # To do：在搜索txt的时候，就把坐标导出来
    def process_contents(self, f_item, root):
        item_struct = None
        item_path = os.path.join(root, f_item)
        if f_item.endswith(".xlsx") or f_item.endswith(".xls"):
            _content = pd.read_excel(item_path, nrows=None, header=None, index_col=False).to_json(orient="values")
            inter_page = int(root.split(os.sep)[-1][15:18])  # Update page value based on the parent folder name
            file_name = root.split(os.sep)[-1][:14]  # Update page value based on the parent folder name

            match = re.search(r'\[(.*?)\]', f_item)
            if match:
                values = match.group(1).split(', ')
                values = [int(value) for value in values]
            else:
                values = []

            # 获取图片的信息
            image_width = 0
            image_height = 0
            parent_dir = os.path.dirname(root)
            image_files = [file for file in os.listdir(parent_dir) if file.endswith(".jpg")]
            result = self.process_locations(image_files[0])
            boxX, boxY, boxW, boxH = map(float, result.split()) # 从文件中读取的大表格的信息

            if image_files:
                image_file = image_files[0]
                image_path = os.path.join(parent_dir, image_file)
                image = Image.open(image_path)
                image_width, image_height = image.size
            picture_width = image_width / boxW;
            picture_height = image_height / boxH;
            # 坐标数组
            ratios = []

            # 计算标记框2相对于图像的中心点坐标

            center_x2 = (boxX * picture_width - image_width / 2 + (values[2] - values[0]) / 2 + values[0]) / picture_width;
            center_y2 = (boxY * picture_height - image_height / 2 + (values[3] - values[1]) / 2 + values[1]) / picture_height;

            # 计算标记框2相对于图像的中心点的宽高
            width_ratio = (values[2] - values[0]) / picture_width
            height_ratio = (values[3] - values[1]) / picture_height

            ratios.append(center_x2)
            ratios.append(center_y2)
            ratios.append(width_ratio)
            ratios.append(height_ratio)
            item_struct = DataModelStruct.content_model(
                name=f_item,
                content_type='table',
                content=_content,
                content_location=' '.join(str(ratio) for ratio in ratios),
                redis_key_value='',
                file_name=file_name,
                page_inner=inter_page
            )
            self.database_dataframe['Contents'].append(item_struct)
        if f_item.startswith("A020") and f_item.endswith(".txt") and not "processing_list" in root.split(os.sep):
            file = f_item.split('.')[0][:14]
            # print(f_item)
            page_inner = int(f_item.split('.')[0][15:18])
            # print(page_inner)
            item_struct = DataModelStruct.content_model(
                name=f_item,
                content_type='text',
                content="'" + str(open(item_path, 'r', encoding='utf-8').read()) + "'",
                content_location="'" + self.process_locations(f_item) + "'",
                redis_key_value='',
                file_name = file,
                page_inner=page_inner
            )
            self.database_dataframe['Contents'].append(item_struct)
        elif f_item.startswith("A020") and (f_item.endswith(".jpg") or f_item.endswith(".png")):
            if 'processing_list' in root:
                self.process_images(f_item, item_path, 1)
            elif 'processed_list' in root:
                self.process_images(f_item, item_path, 0)


   # to do: 如何优化 取消该loop
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
                            if f_item.endswith(".jpg"):
                                text_content = self.read_file_lines_descending(txt_file, txt_file_path)
                                return text_content
                            else:
                                text_content = self.read_file_lines_ascending(txt_file, txt_file_path)
                                return text_content
        return "NULL"

    def read_file_lines_ascending(self, file, file_path):
        line_count = self.read_line_count.get(file_path, 0)  # 获取已读取行数，默认为0
        lines = file.readlines()
        text_content = lines[line_count].strip()  # 根据行数读取文件内容
        self.read_line_count[file_path] = line_count + 1  # 将已读取行数加一保存
        # 去除单引号、开头的0和空格
        text_content = text_content.replace("'", "").lstrip("0").lstrip()
        return text_content

    def read_file_lines_descending(self, file, file_path):
        lines = file.readlines()
        lines.reverse()  # Reverse the order of lines
        line_count = self.read_line_count.get(file_path, 0)  # 获取已读取行数，默认为0
        text_content = lines[line_count].strip()  # Read the line based on line count
        text_content = text_content.replace("'", "").lstrip("1").lstrip()
        return text_content


class DataSync(DataProcess):
    def create_path(self, row, root_id):
        with get_db_session_sql('predict') as session:
            # 判定是否为root
            if row[1] == 1:
                record = PathInfo(
                    path_name=row[0],
                    depth=row[1],
                    father_id=root_id,
                    abs_path=row[2],
                    create_time=datetime.datetime.now(),
                    last_update_time=datetime.datetime.now(),
                )
                # print(record)
                session.add(record)
            else:
                check_record = (
                    session.query(PathInfo)
                    .filter(PathInfo.path_name == row[2].rsplit(os.sep)[-1])
                    .filter(PathInfo.depth == row[1] - 1)
                    .filter(PathInfo.abs_path == row[2].rsplit(os.sep, 1)[0])
                    .one_or_none()
                )
                if check_record:
                    record = PathInfo(
                        path_name=row[0],
                        depth=row[1],
                        father_id=check_record.id,
                        abs_path=row[2],
                        create_time=datetime.datetime.now(),
                        last_update_time=datetime.datetime.now(),
                    )
                    session.add(record)

            try:
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            return record

    def create_file(self, row):
        with get_db_session_sql('predict') as session:
            check_record = (
                session.query(PathInfo)
                .filter(PathInfo.path_name == row[1].rsplit(os.sep, 1)[1])
                .filter(PathInfo.abs_path == row[1].rsplit(os.sep, 1)[0])
                .one_or_none()
            )
            if check_record:
                record = FileInfo(
                    file_name=row[0],
                    father_path=check_record.id,
                    create_time=datetime.datetime.now(),
                    last_update_time=datetime.datetime.now(),
                )
                session.add(record)

                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                return record

    def create_image(self, row):
        with get_db_session_sql('predict') as session:
            check_record = (
                session.query(FileInfo)
                .filter(FileInfo.file_name == row[-2])
                .one_or_none()
            )
            if check_record:
                record = PageImagesInfo(
                    page_name=row[0],
                    page_inner_id=row[1],
                    father_Path = check_record.id,
                    image_url = row[2],
                    image_height = row[3],
                    image_width = row[4],
                    redis_key_value = row[5],
                    sub_page = row[-1],
                    create_time=datetime.datetime.now(),
                    last_update_time=datetime.datetime.now(),
                )
                session.add(record)

                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
                return record

    def create_content(self, row):

        with get_db_session_sql('predict') as session:
            check_record_file = (
                session.query(FileInfo)
                .filter(FileInfo.file_name == row[-2])
                .one_or_none()
            )
            if check_record_file:

                check_page = (
                    session.query(PageImagesInfo)
                    .filter(PageImagesInfo.father_Path == check_record_file.id)
                    .filter(PageImagesInfo.page_inner_id == row[-1])
                    .filter(PageImagesInfo.sub_page == 1)
                    .one_or_none()
                )

                if check_page:

                    record = Contents(
                        name=row[0],
                        content_type=row[1],
                        father_file=check_record_file.id,
                        father_page=check_page.id,
                        content=row[2],
                        content_location=row[3],
                        redis_key_value=row[4],
                        source=row[5],
                        is_active=row[6],
                        create_time=datetime.datetime.now(),
                        last_update_time=datetime.datetime.now(),
                    )
                    session.add(record)

                    try:
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        raise e
                    return record

    def database_updata(self, root_id):
        # 录入数据库
        with get_db_session_sql('predict') as session:
            # 处理 paths
            for row in self.database_dataframe["Paths"]:
                record = (
                    session.query(PathInfo)
                    .filter(PathInfo.path_name == row[0])
                    .filter(PathInfo.depth == row[1])
                    .filter(PathInfo.abs_path == row[2])
                    .one_or_none()
                )
                if not record:
                    record = self.create_path(row, root_id)

            # release memory
            del self.database_dataframe["Paths"]
            self.path_tree = None
            self.path_depth = None

            # 处理files
            for row in self.database_dataframe["Files"]:
                record = (
                    session.query(FileInfo)
                    .filter(FileInfo.file_name == row[0])
                    .one_or_none()
                )
                if not record:
                    record = self.create_file(row)

            del self.database_dataframe["Files"]
            self.file_page = None

            # 处理 pageImages
            for row in self.database_dataframe["PageImages"]:
                record = (
                    session.query(PageImagesInfo)
                    .filter(PageImagesInfo.page_name == row[0])
                    .filter(PageImagesInfo.page_inner_id == row[1])
                    .filter(PageImagesInfo.image_url == row[2])
                    .filter(PageImagesInfo.redis_key_value == row[5])
                    .one_or_none()
                )
                if not record:
                    record = self.create_image(row)

            del self.database_dataframe["PageImages"]
            self.sub_page = None

            for row in self.database_dataframe["Contents"]:
                record = (
                    session.query(Contents)
                    .filter(Contents.name == row[0])
                    .filter(Contents.content_type == row[1])
                    .one_or_none()
                )
                if not record:
                    record = self.create_content(row)

            del self.database_dataframe["Contents"]
        logging.info(f"数据入库成功")

    def run_update_sync(self, folder_path=None):
        root_id = -1
        if self.root_path and not folder_path:
            folder_path = self.root_path

        root_dir = self.root_path.rsplit(os.sep)[-1].replace("\\","/")
        root_data = DataModelStruct.path_model(self.root_name, 1, root_dir)
        self.database_dataframe['Paths'].append(root_data)
        try:
            self.process_paths(folder_path)
            logging.info(f"格式化数据成功 - 检测到{len(self.database_dataframe['Paths'])}条paths数据 - "
                         f"{len(self.database_dataframe['Files'])}条Files数据 - {len(self.database_dataframe['PageImages'])}条Images数据 - "
                         f"{len(self.database_dataframe['Contents'])}条Contents数据")
        except Exception as e:
            logging.info(e)
            logging.info("格式化数据失败")

        self.database_updata(root_id)




if __name__ == "__main__":
    engine = DataSync(root)
    logging.info(f"开始同步数据")
    engine.run_update_sync()
    # pprint(engine.database_dataframe["Paths"])
    # pprint(engine.database_dataframe["Files"])
    # print(len(engine.database_dataframe["PageImages"]))
    # pprint(engine.database_dataframe["PageImages"])
    # pprint(engine.database_dataframe['Contents'])
    # for row in engine.database_dataframe["Contents"]:
    #     print(row[-2])
    # pprint(engine.path_tree)
