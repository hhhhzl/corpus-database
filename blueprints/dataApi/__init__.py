import datetime
from pprint import pprint

# from blueprints.dataApi.controllers import (AccountController,
#                                             UserAssetHistController,
#                                             UserConfigController)
from flask import Blueprint, request
from utils import iso_ts
from utils.response_tools import (SuccessDataResponse)

bp = Blueprint('data_api', __name__, url_prefix='/api/data_api')


def data_fetch_helper(user_number):
    if user_number == 1:
        # 查找postgres
        pass
    else:
        # 查找redis merge postgres
        pass


@bp.route('cash', methods=['POST'])
def get_data():
    data = 5000
    return SuccessDataResponse(data)
