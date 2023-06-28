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
@bp.route('fetch_path/<path_id>/', methods=['GET'])
def fetch_path(path_id):
    try:
        data = DataController._search_path_file(id=path_id)
        return SuccessDataResponse(data)
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')


@bp.route('fetch_page/<file_id>/', methods=['GET'])
def fetch_page(file_id):
    try:
        data = DataController._search_file_page(id=file_id)
        return SuccessDataResponse(data)
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')

@bp.route('fetch_content', methods=['POST'])
def fetch_content():
    try:
        args = request.json
        image_id = args.get('image_id')
        uuid = args.get('uuid')
        data = DataController._search_content(image_id=image_id, uuid=uuid)
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
    # ['content_type']
    #  ['father_page'] (id)
    # ['content']
    # ['location']
    try:

        args = request.json

        dic = {
            "name":args.get('name'),
            'content':args.get('content'),
            'content_type':args.get('content_type'),
            'content_location':args.get('content_location'),
            'father_page':args.get('father_page')
        }

        response = DataController._add_content(
            row=dic
        )

        if response and type(response) == bool:
            return SuccessDataResponse([])
        else:
            return ArgumentExceptionResponse(msg=f'{response}')
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')

# 悲观锁服务
@bp.route('lock', methods=['POST'])
def lock():
    args = request.json
    try:
        image_id = args.get("image_id")
    except:
        return ArgumentExceptionResponse(msg=f'No Image Provide.')

    try:
        uuid_ = args.get("uuid")
    except:
        uuid_ = None

    redis_cli = RedisWrapper('p_lock')
    value = redis_cli.get(f'predict:lock:{image_id}')

    # 有锁
    if value:
        # 无uuid或uuid不匹配，无法解锁
        if not uuid_ or uuid_ != value:
            return ArgumentExceptionResponse(msg=f'Image locked.')
        # uuid匹配，延续解锁时长3s
        elif uuid_ == value:
            redis_cli.set(key=f'predict:lock:{image_id}', ex=4, value=value)
            return SuccessDataResponse([])

    else:
        uuid_id = u.uuid4()
        redis_cli.set(key=f'predict:lock:{image_id}', ex=4, value=str(uuid_id))
        return SuccessDataResponse(str(uuid_id))

@bp.route('delete_content/<content_id>/', methods=['GET'])
def delete_content(content_id):
    try:
        response = DataController._delete_content(
            id=content_id
        )

        if response and type(response) == bool:
            return SuccessDataResponse([])
        else:
            return ArgumentExceptionResponse(msg=f'{response}')
    except Exception as e:
        return ArgumentExceptionResponse(msg=f'{e}')


@bp.route('test', methods=['GET'])
def test():
    return SuccessDataResponse([])

