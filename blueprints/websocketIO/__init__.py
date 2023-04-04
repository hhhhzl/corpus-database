from flask import (
    Blueprint, request, Flask, redirect, request, jsonify, url_for, render_template, session
)
from flask_socketio import (
    SocketIO, join_room, leave_room, emit
)
from configs.management_app_config import room_name, constData
from utils import abspath
from utils.response_tools import ArgumentExceptionResponse, SuccessDataResponse
from utils.logger_tools import get_general_logger
import json
from werkzeug.utils import secure_filename
import pymysql
import os
import uuid
from pymysql.converters import escape_string
import re
import csv

logger = get_general_logger(name='general_info', path=abspath('logs', 'server'))
bp = Flask(__name__, static_folder=abspath('templates', 'assets'),
           template_folder=abspath('templates'))
bp.debug = True
bp.config['SECRET_KEY'] = 'secret'
bp.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(bp, manage_session=False)
clients = []


def getDBConnection():
    return pymysql.connect(host='0.0.0.0', user='root', password='Mysql@60003', database='Corpus_STA_DB')


@socketio.on('join', namespace='/main')
def join(message):
    room = session.get('room')
    join_room(room)
    global clients
    clients.append(session.get('username'))
    emit("users", {"user_count": clients}, broadcast=True)
    emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/main')
def text(message):
    room = session.get('room')
    emit('message', {'msg': session.get('username') + ' : ' + json.dumps(message['msg']), 'data': message['msg']},
         room=room)


@socketio.on('left', namespace='/main')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()
    global clients
    clients.remove(username)
    emit("users", {"user_count": clients}, broadcast=True)
    emit('status', {'msg': username + ' has left the room.'}, room=room)


# functions for render responses for app1
@bp.route("/", methods=['GET'])
def home():
    return render_template("login.html")


@bp.route("/main", methods=['POST', 'GET'])
def main():
    if request.method == "POST":
        username = request.form["username"]
        global clients
        if username:
            if username not in clients:
                session['username'] = username
                session['room'] = room_name
                return render_template("orders.html", index=None, session=session, data=constData, cur=1, all=1)
            else:
                return redirect(url_for("home"))

        else:
            return redirect(url_for("home"))
    else:
        if session.get('username') is not None:
            return render_template('orders.html', session=session)
        else:
            return redirect(url_for('home'))


# numInPage = 20
numInPage = 5


# @bp.route("/count", methods=['GET'])
# def count():
#     #     db = getDBConnection()
#     #     cursor = db.cursor()
#     #     sql = "select count(*) from word_segmentation"
#     #     print(sql)
#     #     cursor.execute(sql)
#     #     result = cursor.fetchall()
#     #     return str(result[0][0] // numInPage + 1)
#     print(str(len(constData) // numInPage + 1))
#     return str(len(constData) // numInPage + 1)


#
#
# @bp.route("/find", methods=['GET'])
# def find():
#     db = getDBConnection()
#     page = int(request.args.get("pageNum")) - 1
#     partOfSpeech = request.args.get("partOfSpeech")
#     cursor = db.cursor()
#     if partOfSpeech is None or partOfSpeech == "1":
#         sql = "select * from word_segmentation limit {},{}".format(page * numInPage, numInPage)
#     else:
#         sql = "select * from word_segmentation where part_of_speech='{}' limit {},{}".format(partOfSpeech,
#                                                                                              page * numInPage,
#                                                                                              numInPage)
#     print(sql)
#     cursor.execute(sql)
#     result = cursor.fetchall()
#     return jsonify(result)
#
#
# @bp.route("/upload", methods=['POST'])
# def upload():
#     db = getDBConnection()
#     # file为上传表单的name属性值
#     f = request.files['file']
#     fname = secure_filename(f.filename)
#     ext = fname.rsplit('.')[-1]
#     # 生成一个uuid作为文件名
#     fileName = str(uuid.uuid4()) + "." + ext
#     # os.path.join拼接地址，上传地址，f.filename获取文件名
#     f.save(os.path.join(bp.config['UPLOAD_FOLDER'], fileName))
#
#     f = open(os.path.join(bp.config['UPLOAD_FOLDER'], fileName), 'r', encoding='utf-8')
#     cursor = db.cursor()
#     # for item in f.readlines():
#
#     reader = csv.reader(f)
#     for row in reader:
#         val = row[1].replace("\n", "")
#         sql = "insert into word_segmentation(english) values('{}')".format(escape_string(val))
#         print(sql)
#         cursor.execute(sql)
#         db.commit()
#         #  for word in item:
#         #     if "/n" in word:
#         #         if "/nt" in word:
#         #           word=word.replace("/nt","")
#         #           flag="机构团体"
#         #         elif "/ns" in word:
#         #           flag="地名"
#         #           word=word.replace("/ns","")
#         #         elif "/nr" in word:
#         #           flag="人名"
#         #           word=word.replace("/nr","")
#         #         elif "/nx" in word:
#         #           flag='科技名词'
#         #           word=word.replace("/nx","")
#         #         else:
#         #           flag="科技名词"
#         #           word=word.replace("/n","")
#         #         rstr= r"[\、\/\\\:\*\?\"\<\>\|\(\)\（\）]"  # '/ \ : * ? " < > |'
#         #         word = re.sub(rstr, "", word)
#         #         word=word.strip()
#         #         if len(word)==0 or len(word)==1 or word.isdigit() or word[0].isdigit():
#         #           continue
#
#         #         sql=f'''select * from word_segmentation where word='{escape_string(word)}' or abbreviation='{escape_string(word)}' '''
#         #         cursor.execute(sql)
#         #         print(sql)
#         #         results = cursor.fetchall()
#         #         if len(results) !=0:
#         #             print("已存在")
#         #             continue
#         #         if word.encode('utf-8').isalpha():
#         #             sql="insert into word_segmentation(abbreviation,part_of_speech) values('{}','{}')".format(escape_string(word),flag)
#         #         else:
#         #             sql="insert into word_segmentation(word,part_of_speech) values('{}','{}')".format(escape_string(word),flag)
#         #         print(sql)
#         #         cursor.execute(sql)
#         #         db.commit()
#     f.close()
#
#     os.remove(os.path.join(bp.config['UPLOAD_FOLDER'], fileName))
#     return 'ok'
def start():
    socketio.run(bp, port=60004, debug=True)


if __name__ == "__main__":
    start()
