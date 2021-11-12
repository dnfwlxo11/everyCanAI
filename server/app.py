# -*- coding: utf-8 -*-

import json
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import inference
import base64
from flask_mail import Mail, Message
import config
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


# 한글 깨짐 해결 설정
app.config['JSON_AS_ASCII'] = False

calorieDBPath = './calorieDB/food_cal.json'

# Email 설정
mail_settings = config.getMailInfo()

app.config.update(mail_settings)

# args : (classes 배열, scores 배열, 원하는 score의 정도)
def parseCalorieDB(classes, scores, score):
    with open(calorieDBPath, 'r') as jsonFile:
        calData = ''
        calData = json.load(jsonFile)

        cnt = 1
        parseResult = []
        for _class, _score in zip(classes, scores):
            if _score >= score:
                parseResult.append({'rank': cnt, 'food': _class, 'score': _score * 100, 'cal': calData[_class]})
                cnt+=1

        return parseResult

# sender = email, receiver = email, content = string or object
def send_email(senders, receiver, content):
    try:
        mail = Mail(app)
        msg = Message('Title', sender = senders, recipients = receiver)
        msg.body = str(content)
        mail.send(msg)
        return True
    except Exception:
        return False

@app.route('/api', methods=['GET'])
def hello():
    if request.method == 'GET':
        try:
            return {'success': True, 'msg': '정상적으로 서버 동작 중'}
        except Exception as e:
            return {'success': False, 'msg': 'GET 요청 테스트 중 에러가 발생했습니다.', 'error': e}

@app.route('/api/upload', methods=['POST'])
def fileUpload():
    if request.method == 'POST':
        try:
            return {'success': True, 'msg': '서버에 학습 이미지 업로드가 완료되었습니다.'}
        except Exception as e:
            return {'success': False, 'msg': '이미지 업로드 중 에러가 발생했습니다.', 'error': e}

@app.route('/api/information', methods=['GET'])
def modelInfo():
    if request.method == 'GET':
        try:
            return {'success': True, 'info': '레이어 : ~~개, input: [224, 224, 3], 예시'}
        except Exception as e:
            return {'success': False}

@app.route('/api/mail', methods=['POST'])
def sendMail():
    if request.method == 'POST':
        try:
            body = json.loads(request.get_data().decode('utf-8'))
            senders = body['sender']
            receiver = body['reciver']

            content = body['content']
            content = ('코멘트 : {}\n음식명 : {}\n칼로리 : {}\n정확도 : {}').format(content['msg'], content['food'], content['kcal'], content['conf'])

            receiver = receiver.split(',')
        
            for i in range(len(receiver)):
                receiver[i] = receiver[i].strip()
        
            # 칼로리, 단백질, 지방, 탄수화물
            result = send_email(senders, receiver, content)
            print(result, 'result')

            if not result:
                return {'success': False, 'msg': '메일이 보내지지 않았습니다.'}
            else:
                return {'success': True, 'msg': '메일이 정상적으로 보내졌습니다.'}
        except Exception as e:
            return {'success': False, 'msg': '메일 전송 중 에러가 발생했습니다.', 'error': e}

@app.route('/api/save', methods=['POST'])
def saveImage():
    if request.method == 'POST':
        try:
            file = request.files['file']
            file.save(secure_filename(file.filename))

            return {'success': True, 'msg': '이미지가 정상적으로 저장 되었습니다.'}
        except Exception as e:
            return {'success': False, 'msg': '이미지 저장 테스트 중 에러가 발생했습니다.', 'error': e}


@app.route('/api/inference', methods=['POST'])
def getImage():
    if request.method == 'POST':
        try:
            # 웹 버전
            data = request.get_data().decode('utf-8').replace('data:image/png;base64,', '')
            data = base64.b64decode(data)

            # Api 버전
            # data = request.files['file'].read()

            predict = inference.run_inference_on_image(data)
            result = parseCalorieDB(predict['classes'], predict['scores'], 0.3)

            return {'success': True, 'msg': '이미지를 정상적으로 분류하였습니다.', 'predict': result}
        except Exception as e:
            return {'success': False, 'msg': '추론도중 에러가 발생했습니다.', 'error': e}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)