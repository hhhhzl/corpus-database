import datetime
from pprint import pprint

from blueprints.dataApi.controllers import DataController
from flask import Blueprint, request
from utils import iso_ts
from utils.response_tools import (SuccessDataResponse)
from flask import jsonify

bp = Blueprint('data_api', __name__, url_prefix='/api/data_api')

@bp.route('fetch_corpus', methods=['POST'])
def fetch_corpus():
    page = 1
    data = DataController.fetch_corpus_data(page = page)
    # cols = ['id', 'noun', 'eng_name', 'attributes', 'abb']
    # result = [{col: getattr(d, col) for col in cols} for d in data]
    return SuccessDataResponse(data)

@bp.route('test', methods=['GET'])
def test():
    return 'hello'
