import datetime
from pprint import pprint

from blueprints.dataApi.controllers import DataController
from flask import Blueprint, make_response, request, current_app
from utils import iso_ts
from utils.response_tools import (SuccessDataResponse, ArgumentExceptionResponse)
from flask import jsonify
from datetime import timedelta
from functools import update_wrapper

bp = Blueprint('data_api', __name__, url_prefix='/api/data_api')

@bp.route('fetch_corpus', methods=['POST'])
def fetch_corpus():
    args = request.json
    page = args.get('page')
    if page > 0:
        data = DataController.fetch_corpus_data(page = page)
        response = SuccessDataResponse(data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        response = ArgumentExceptionResponse(msg='wrong page index.')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@bp.route('fetch_subject', methods=['POST'])
def fetch_subject():
    args = request.json
    page = args.get('page')
    if page > 0:
        data = DataController.fetch_subject_data(page = page)
        response = SuccessDataResponse(data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    else:
        response = ArgumentExceptionResponse(msg='wrong page index.')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
@bp.route('test', methods=['GET'])
def test():
    return 'hello'
