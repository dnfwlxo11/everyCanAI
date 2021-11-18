# -*- coding: utf-8 -*-

import json
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import inference
import base64
import os
import time
from flask_cors import CORS
import retrain_inceptionV3 as retrain
from asyncFlask.job import test, train

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# 한글 깨짐 해결 설정
app.config['JSON_AS_ASCII'] = False

def parsePredict(classes, scores, conf):
    result = []
    for i, j in zip(classes, scores):
        if (j >= conf):
            result.append([i, round(j*100, 2)])

    return result

def makeDirectory(files):
    # 현재 시간으로 폴더를 만듦
    now = time.localtime()
    dirName = '{}{}{}_{}{}{}'.format(now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

    if not os.path.exists('./db/{}'.format(dirName)):
        os.makedirs('./db/{}'.format(dirName))

    # 각 클래스별 폴더 생성
    # os.chdir('./db/{}'.format(dirName))
    for i in files['classes']:
        className = './db/{}/{}'.format(dirName, i)
        if not os.path.exists(className):
            os.makedirs(className)

        for j in range(len(files[i])):
            file = files[i][j]['src']
            fileName = '{}/{}'.format(className, str(i) + '_' + str(j) + '.png')
            image = base64.b64decode(str(file.split(',')[1]))
            with open(fileName, 'wb') as f:
                f.write(image)

    return {'path': './db/{}'.format(dirName)}

@app.route('/api', methods=['GET'])
def hello():
    if request.method == 'GET':
        try:
            return {'success': True, 'msg': '정상적으로 서버 동작 중입니다.'}
        except Exception as e:
            return {'success': False, 'msg': 'GET 요청 테스트 중 에러가 발생했습니다.', 'error': e}

@app.route('/api/models', methods=['GET'])
def loadModels():
    if request.method == 'GET':
        try:
            result = []
            path = './models'

            modelList = os.listdir(path)
            modelList.remove('imagenet')

            for i in modelList:
                modelFiles = os.listdir('{}/{}'.format(path, i))
                if 'output_graph.pb' in modelFiles:
                    result.append({'name': i, 'progress': '학습 완료'})
                else:
                    result.append({'name': i, 'progress': '학습 중'})

            return {'success': True, 'msg': '모델 목록을 불러오는데 성공했습니다.', 'models': result}
        except Exception as e:
            return {'success': False, 'msg': '모델 목록을 불러오는 중 에러가 발생했습니다.', 'error': e}


@app.route('/api/upload', methods=['POST'])
def fileUpload():
    if request.method == 'POST':
        try:
            data = request.get_json()

            path = makeDirectory(data)

            return {'success': True, 'msg': '서버에 학습 이미지 업로드가 완료되었습니다.', 'path': path}
        except Exception as e:
            return {'success': False, 'msg': '이미지 업로드 중 에러가 발생했습니다.', 'error': e}

@app.route('/api/information', methods=['GET'])
def modelInfo():
    if request.method == 'GET':
        try:
            return {'success': True, 'info': '레이어 : ~~개, input: [224, 224, 3], 예시'}
        except Exception as e:
            return {'success': False}

@app.route('/api/train', methods=['POST'])
def modelTrain():
    if request.method == 'POST':
        try:
            imagePath = request.get_json()['path']

            result = train.delay(imagePath)
            print(result)

            return {'success': True, 'msg': '학습 요청을 완료했습니다.', 'job_id': str(result)}
        except Exception as e:
            return {'success': False, 'error': e}

@app.route('/api/redis', methods=['POST'])
def redisTest():
    if request.method == 'POST':
        result = test.delay(1,4)
        return {'success': True}

@app.route('/api/inference', methods=['POST'])
def getImage():
    if request.method == 'POST':
        try:
            # base64 버전
            # data = request.get_data().decode('utf-8').replace('data:image/png;base64,', '')
            # data = base64.b64decode(data)

            # blob 버전
            data = request.files['file'].read()

            predict = inference.run_inference_on_image(data)
            result = parsePredict(predict['classes'], predict['scores'], 0.3)

            return {'success': True, 'msg': '이미지를 정상적으로 분류하였습니다.', 'predict': result}
        except Exception as e:
            return {'success': False, 'msg': '추론도중 에러가 발생했습니다.', 'error': e}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
