import datetime
from pprint import pprint

from blueprints.dataApi.controllers import DataController
from flask import Blueprint, request
from utils import iso_ts
from utils.response_tools import (SuccessDataResponse, ArgumentExceptionResponse)
from flask import jsonify

bp = Blueprint('data_api', __name__, url_prefix='/api/data_api')

@bp.route('fetch_corpus', methods=['POST'])
def fetch_corpus():
    args = request.json
    page = args.get('page')
    if page > 0:
        data = DataController.fetch_corpus_data(page = page)
        return SuccessDataResponse(data)
    else:
        return ArgumentExceptionResponse(msg='wrong page index.')

@bp.route('fetch_subject', methods=['POST'])
def fetch_subject():
    args = request.json
    page = args.get('page')
    if page > 0:
        data = DataController.fetch_subject_data(page = page)
        return SuccessDataResponse(data)
    else:
        return ArgumentExceptionResponse(msg='wrong page index.')
@bp.route('test', methods=['GET'])
def test():
    return 'hello'
