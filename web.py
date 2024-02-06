from doctest import debug
from flask import Flask, render_template, request, redirect, url_for, session, make_response, g,jsonify,send_file
import time
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
import randomstring,os
import ast
import httpx
import requests
import json
import io
from datetime import datetime
import pytz
APISITE = "https://battlecats-api.onrender.com"
app = Flask(__name__)
app.secret_key = 'vBNcpecpWCYZG9xNvrl0DITGL4Xwc93I'

def check_cookies(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        license_key = request.cookies.get('license')
        if not license_key:
            return redirect('/')
        return func(*args, **kwargs)
    return wrapped
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('licenses.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        license_key = request.form.get('license')
        with app.app_context():

            c = get_db().cursor()
            row = c.execute("SELECT * FROM licenses WHERE license=?", (license_key,)).fetchone()

            if row is None:
                return "<script>alert('유효하지 않은 라이센스입니다.'); window.location.href='/';</script>"
            
            result = row
            response = make_response(render_template('main.html', license=result[0], number=result[1]))
            
            response.set_cookie('license', result[0])
            response.set_cookie('number', result[1])

            # Check for automatic login
                
            return response

    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is not None:
                    
                    result = db_row
                    response = make_response(render_template('main.html', message="로그인 성공",license=result[0], number=result[1]))
                    response.set_cookie('license', result[0])
                    response.set_cookie('number', result[1])  
                    return response
                else:
                    return render_template('login.html')

        else:
            return render_template('login.html')
    return render_template('login.html')
def search_in_file(keyword):
    if keyword is None:  # keyword가 None인지 확인
        keyword = ""
    result = []
    with open('id.txt', 'r', encoding='utf-8') as file:
        for line in file:
            id, text = line.strip().split('\t')
            if keyword in text:
                _id = int(id) + 1
                formatted_id = f"https://onestoppress.com/images/{_id:03d}-1_square.png"
                result.append((int(id), formatted_id, text))
    return result
@app.route('/searchid', methods=['GET', 'POST'])
def searchid():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('searchid.html')
        else:
            return make_response(redirect('/'))
    if request.method == 'POST':
        data = request.get_json(force=True)
        name = data['name']
        data = search_in_file(name)
        return jsonify(data=data)



@app.route('/edit', methods=['GET', 'POST'])
@check_cookies
def edit():
    if request.method == 'GET':
        return render_template('main.html')
@app.route('/logout', methods=['POST','GET'])
def logout():
    response = make_response(redirect('/'))  # Redirect to login page after logout
    response.set_cookie('number', '', expires=datetime.utcnow() - timedelta(days=1))
    response.set_cookie('session', '', expires=datetime.utcnow() - timedelta(days=1))
    response.set_cookie('license', '', expires=datetime.utcnow() - timedelta(days=1))
    return response
@app.route('/myaccount', methods=['POST','GET'])
def myaccount():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                result = db_row
            else:
                return "<script>window.location.href='/';</script>"
            response = make_response(render_template('myaccount.html', license=result[0], number=result[1]))
            response.set_cookie('license', result[0])
            response.set_cookie('number', result[1])
            return response
    else:
        return "<script>window.location.href='/';</script>"

@app.route('/contact', methods=['POST','GET'])
def contact():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                return render_template('contact.html')
            else:
                return make_response(redirect('/'))
    else:
        return make_response(redirect('/'))


@app.route('/history', methods=['GET'])
@check_cookies
def history():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row[3] is not None:
                account = ast.literal_eval(db_row[3])
            else:
                account = ["저장된 계정 정보 없음","저장된 계정 정보 없음","저장된 계정 정보 없음"]
    return render_template('history.html', transfer_code=account[0], pin=account[1], time=account[2])

@app.route('/admin', methods=['GET'])
def admin():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                if db_row[0] == "webeditor":
                    return render_template('admin_dashboard.html')

                else:
                    return "<script>alert('접근 권한 없음');javascript:history.back();</script>"
            else:
                return "<script>window.location.href='/';</script>"

    else:
        return "<script>alert('알 수 없는 오류가 발생했습니다.');javascript:history.back();</script>"
@app.route('/coin_edit', methods=['POST'])
def coin_edit():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                if db_row[0] == "webeditor":
                    license = request.form.get('license_1')
                    new_coin_ = request.form.get('coin_value_1')
                    new_coin = int(db_row[1]) + int(new_coin_)
                    row = c.execute("SELECT * FROM licenses WHERE license=?", (license,)).fetchone()
                    if row is None:
                        return "<script>alert('라이센스 정보를 찾을 수 없습니다.');javascript:history.back();</script>"
                    c.execute("UPDATE licenses SET number=? WHERE license=?", (str(new_coin), license))
                    get_db().commit()
                    return "<script>alert('완료');javascript:history.back();</script>"
                else:
                    return "<script>alert('접근 권한 없음');javascript:history.back();</script>"
            else:
                return "<script>window.location.href='/';</script>"

    else:
        return "<script>alert('알 수 없는 오류가 발생했습니다.');javascript:history.back();</script>"
@app.route('/license_del', methods=['POST'])
def license_del():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                if db_row[0] == "webeditor":
                    license = request.form.get('license_2')
                    row = c.execute("SELECT * FROM licenses WHERE license=?", (license,)).fetchone()
                    if row is None:
                        return "<script>alert('라이센스 정보를 찾을 수 없습니다.');javascript:history.back();</script>"
                    c.execute("DELETE FROM licenses WHERE license=?", (license,))
                    get_db().commit()
                    
                    return "<script>alert('완료');javascript:history.back();</script>"
                else:
                    return "<script>alert('접근 권한 없음');javascript:history.back();</script>"
            else:
                return "<script>window.location.href='/';</script>"

    else:
        return "<script>alert('알 수 없는 오류가 발생했습니다.');javascript:history.back();</script>"
@app.route('/downloaddb', methods=['POST', 'GET'])
def downloaddb():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                if db_row[0] == "webeditor":
                        response = send_file('licenses.db', as_attachment=True)
                        response.headers["Content-Disposition"] = "attachment; filename=licenses.db"
                        return response
                else:
                    return "<script>alert('접근 권한 없음');javascript:history.back();</script>"
            else:
                return "<script>window.location.href='/';</script>"

    else:
        return "<script>alert('알 수 없는 오류가 발생했습니다.');javascript:history.back();</script>"
@app.route('/license_create', methods=['POST'])
def license_create():
    count = 0
    if 'license' in request.cookies:
        with app.app_context():
            c = get_db().cursor()
            cookie_license=request.cookies.get('license')
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                if db_row[0] == "webeditor":
                    number = int(request.form.get('license_3'))
                    number_value = int(request.form.get('coin_value_3'))
                    codes = []
                    for _ in range(number):
                        code = randomstring.pick(20)
                        codes.append(code)
                        c.execute("INSERT INTO licenses (license, number) VALUES (?, ?)", (code, number_value))
                        get_db().commit()
                        result = "<br>".join(codes)
                    return render_template('licenses.html',licenses=result)
                else:
                    return "<script>alert('접근 권한 없음');javascript:history.back();</script>"
            else:
                return "<script>window.location.href='/';</script>"

    else:
        return "<script>alert('알 수 없는 오류가 발생했습니다.');javascript:history.back();</script>"
@app.route('/editinfo', methods=['POST','GET'])
def editinfo():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                return render_template('editinfo.html')
            else:
                return "<script>window.location.href='/';</script>"
    else:
        return "<script>window.location.href='/';</script>"
@app.route('/help', methods=['POST','GET'])
def help():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None:
                return render_template('help.html')
            else:
                return "<script>window.location.href='/';</script>"
    else:
        return "<script>window.location.href='/';</script>"
@app.route('/backup', methods=['POST','GET'])
def backup():
    if 'license' in request.cookies:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if db_row is not None and db_row[2] is not None:
                save_stats = json.loads(db_row[2])
                return render_template('backup.html', savestats = save_stats, playtime = f'{save_stats["play_time"]["hh"]}시간 {save_stats["play_time"]["mm"]}분',inquiry_code = save_stats["inquiry_code"])
            else:
                return "<script>alert('저장된 정보가 없거나 라이센스가 올바르지 않습니다.');window.location.href='/';</script>"
    else:
        return "<script>window.location.href='/';</script>"
@app.route('/restore', methods=['POST','GET'])
def restore():
    savestats = request.get_json()['num1']
    if savestats:
        cookie_license=request.cookies.get('license')
        with app.app_context():
            c = get_db().cursor()
            row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
            if row is not None:
                number = int(row[0])
                if number < 3000:
                    data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                    return jsonify(data)
                else:
                    cookie_license=request.cookies.get('license')
                    db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                    savestats = json.loads(db_row[2])
                    data = {"save_stats" : savestats}
                    result = requests.post(f'{APISITE}/edit/restore', json=data).json()
                    if result["result"]:
                        number -= 3000
                        c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                        savestats_str = json.dumps(result["savestats"])
                        c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                        seoul_tz = pytz.timezone('Asia/Seoul')
                        now = datetime.now(seoul_tz)
                        time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                        c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                        get_db().commit()
                        data = {"result" :True, "info" : None}
                        return jsonify(data)
                    else:
                        data = {"result" :False, "info" : result['info']}
                        return jsonify(data)
            else:
                return jsonify({"result" :False, "info" : "라이센스 오류"})
    else:
        return jsonify({"result" :False, "info" : "값 오류"})
@app.route('/catfood', methods=['POST','GET'])
def catfood():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('catfood.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 1000:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num1'], "pin" : data['num2'], "version" : data['num3'],"item":[None],"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/catfood', json=data).json()
                        if result["result"]:
                            number -= 1000
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)

@app.route('/item', methods=['POST','GET'])
def item():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('item.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4'] and data['num5']:
            num5 = json.loads(data['num5'])
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 800:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num2'], "pin" : data['num3'], "version" : data['num1'],"item":num5,"value" : data['num4']}
                        print(data)
                        result = requests.post(f'{APISITE}/edit/item', json=data).json()
                        if result["result"]:
                            number -= 800
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)
@app.route('/catamin', methods=['POST','GET'])
def catamin():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('catamin.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        num5 = json.loads(data['num5'])
        if data['num1'] and data['num2'] and data['num3'] and data['num4'] and data['num5']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 500:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num2'], "pin" : data['num3'], "version" : data['num1'],"item":num5,"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/catamin', json=data).json()
                        if result["result"]:
                            number -= 500
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)
@app.route('/catseye', methods=['POST','GET'])
def catseye():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('catseye.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        num5 = json.loads(data['num5'])
        if data['num1'] and data['num2'] and data['num3'] and data['num4'] and data['num5']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 700:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num2'], "pin" : data['num3'], "version" : data['num1'],"item":num5,"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/catseye', json=data).json()
                        if result["result"]:
                            number -= 700
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)


@app.route('/leadership', methods=['POST','GET'])
def leadership():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('leadership.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 1000:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num2'], "pin" : data['num3'], "version" : data['num1'],"item":[None],"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/leadership', json=data).json()
                        if result["result"]:
                            number -= 1000
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)

@app.route('/getcat', methods=['POST','GET'])
def getcat():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('getcat.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 500:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num2'], "pin" : data['num3'], "version" : data['num1'],"item":[None],"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/cat', json=data).json()
                        if result["result"]:
                            number -= 500
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)


@app.route('/ticket1', methods=['POST','GET'])
def ticket1():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('ticket1.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 500:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num1'], "pin" : data['num2'], "version" : data['num3'],"item":[None],"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/ticket1', json=data).json()
                        if result["result"]:
                            number -= 500
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)
@app.route('/ticket2', methods=['POST','GET'])
def ticket2():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('ticket2.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 700:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num1'], "pin" : data['num2'], "version" : data['num3'],"item":[None],"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/ticket2', json=data).json()
                        if result["result"]:
                            number -= 700
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)
@app.route('/ticket3', methods=['POST','GET'])
def ticket3():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('ticket3.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 800:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num1'], "pin" : data['num2'], "version" : data['num3'],"item":[None],"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/ticket3', json=data).json()
                        if result["result"]:
                            number -= 800
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)
@app.route('/ticket4', methods=['POST','GET'])
def ticket4():
    if request.method == 'GET':
        if 'license' in request.cookies:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                db_row=c.execute("SELECT * FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if db_row is None:
                    return "<script>window.location.href='/';</script>"
                return render_template('ticket4.html')
        else:
            return make_response(redirect('/'))
    elif request.method == 'POST':
        data = request.get_json()
        if data['num1'] and data['num2'] and data['num3'] and data['num4']:
            cookie_license=request.cookies.get('license')
            with app.app_context():
                c = get_db().cursor()
                row = c.execute("SELECT number FROM licenses WHERE license=?", (cookie_license,)).fetchone()
                if row is not None:
                    number = int(row[0])
                    if number < 800:
                        data = {"result" :False, "info" : f"코인이 부족합니다. 잔액 : {number}"}
                        return jsonify(data)
                    else:
                        data = {"transfer" : data['num1'], "pin" : data['num2'], "version" : data['num3'],"item":[None],"value" : data['num4']}
                        result = requests.post(f'{APISITE}/edit/ticket4', json=data).json()
                        if result["result"]:
                            number -= 800
                            c.execute("UPDATE licenses SET number=? WHERE license=?", (str(number), cookie_license))
                            savestats_str = json.dumps(result["savestats"])
                            c.execute("UPDATE licenses SET savestats=? WHERE license=?", (savestats_str, cookie_license))
                            seoul_tz = pytz.timezone('Asia/Seoul')
                            now = datetime.now(seoul_tz)
                            time_string = now.strftime("%Y년 %m월 %d일 %H시 %M분")
                            c.execute("UPDATE licenses SET history=? WHERE license=?", (str([result["transfercode"],result['pin'],time_string]), cookie_license))
                            get_db().commit()
                            data = {"result" :True, "info" : None}
                            return jsonify(data)
                        else:
                            data = {"result" :False, "info" : result['info']}
                            return jsonify(data)
        else:
            data = {"result" :False, "info" : "값을 모두 입력하세요."}
            return jsonify(data)

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")
if __name__ == "__main__":
    with app.app_context():
        c = get_db().cursor()
        c.execute("CREATE TABLE IF NOT EXISTS licenses (license TEXT PRIMARY KEY, number TEXT, savestats TEXT, history TEXT)")
        get_db().commit()
        app.run(debug=True,host='0.0.0.0', port=5000,threaded=False)
