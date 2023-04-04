from collections import Counter
import datetime
import statistics
from configs.postgres_config import get_db_session
from pprint import pprint
import simplejson as json

from utils import abspath
from utils.logger_tools import get_general_logger

logger = get_general_logger('dataApi', path=abspath('logs', 'dataApi'))


class DataController:
    """
    查找流程：
    1。 如果user只有一个，查找post
    2. 如果user多个，查找redis merge

    """

    def __init__(self, user_number):
        self.user_number = user_number


if __name__ == '__main__':
    pass
