from blueprints.dataApi.controllers import DataController
from flask import Blueprint, request
from utils.response_tools import (SuccessDataResponse, ArgumentExceptionResponse)
import json
from utils.redis_tools import RedisWrapper
import uuid as u

bp = Blueprint('data_api', __name__, url_prefix='/api/data_api')

# http://localhost:10981/api/data_api/fetch_root
@bp.route('fetch_root', methods=['GET'])
def fetch_root():
    try:
        data = DataController._search_path_file()
        return SuccessDataResponse(data)
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')

# http://localhost:10981/api/data_api/fetch_path {path_id:int}
@bp.route('fetch_path', methods=['GET'])
def fetch_path():
    args = request.json
    father_id = args.get('path_id')
    try:
        data = DataController._search_path_file(id=father_id)
        return SuccessDataResponse(data)
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')


@bp.route('fetch_page', methods=['GET'])
def fetch_page():
    args = request.json
    father_file_id = args.get('file_id')
    try:
        data = DataController._search_path_file(id=father_file_id)
        return SuccessDataResponse(data)
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')

@bp.route('fetch_content', methods=['GET'])
def fetch_content():
    args = request.json
    father_image_id = args.get('image_id')
    try:
        data = DataController._search_content(image_id=father_image_id)
        return SuccessDataResponse(data)
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')

@bp.route('update_content', methods=['POST'])
def update_content():
    args = request.json
    content_id = args.get('content_id')
    content = args.get('content')
    content_location = args.get('content_location')

    response = DataController._update_content(
        id = content_id,
        content = content,
        location = content_location
    )

    if response and type(response) == bool:
        return SuccessDataResponse([])
    else:
        return ArgumentExceptionResponse(msg=f'{response}')


@bp.route('add_content', methods=['POST'])
def add_content():
    # arg = （
    # ['name'],
    # ['father_file'] (id)
    # ['content_type']
    #  ['father_page'] (id)
    # ['content']
    # ['location']
    args = json.loads(request.json)

    response = DataController._add_content(
        row=args
    )

    if response and type(response) == bool:
        return SuccessDataResponse([])
    else:
        return ArgumentExceptionResponse(msg=f'{response}')

# 悲观锁服务
@bp.route('lock', methods=['POST'])
def lock():
    args = json.loads(request.json)
    if 'image_id' not in args:
        return ArgumentExceptionResponse(msg=f'No Image Provide.')

    image_id = args['image_id']
    redis_cli = RedisWrapper('p_lock')
    value = redis_cli.get(f'predict:lock:{image_id}')

    # 有锁
    if value:
        # 无uuid或uuid不匹配，无法解锁
        if 'uuid' not in args or args['uuid'] != value:
            return ArgumentExceptionResponse(msg=f'Image locked.')
        # uuid匹配，延续解锁时长3s
        elif args['uuid'] == value:
            redis_cli.set(key=f'predict:lock:{image_id}', ex=3, value=value)
            return SuccessDataResponse([])

    else:
        uuid_id = u.uuid4()
        redis_cli.set(key=f'predict:lock:{image_id}', ex=3, value=str(uuid_id))
        return SuccessDataResponse(str(uuid_id))

@bp.route('test', methods=['GET'])
def test():
    return SuccessDataResponse([])

