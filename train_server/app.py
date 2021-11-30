# -*- coding: utf-8 -*-

from flask import Flask, request, send_file, render_template, current_app
import inference
import base64
import os
import time
from flask_cors import CORS
from asyncFlask.job import train
import random
import shutil
import json

os.chdir('/app/train_server')

app = Flask(__name__, static_folder='./static/dist', template_folder='./static/dist', static_url_path='')
app.config.from_object(__name__)

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
    dirName = '{}_{}_{}'.format(random.randrange(1,10000), time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())), random.randrange(1,10000))

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

@app.route('/')
def index():
    return render_template('index.html')

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

            dbPath = './db'
            modelPath = './models'
            outputPath = './output'

            dbList = os.listdir(dbPath)
            modelList = os.listdir(modelPath)
            outputList = os.listdir(outputPath)

            if 'readme.md' in dbList:
                dbList.remove('readme.md')

            for i in dbList:
                if i in outputList:
                    isZip = os.listdir(os.path.join(outputPath, i))
                    modelFiles = os.listdir(os.path.join(modelPath, i))

                    if 'output_graph.pb' in modelFiles and not 'zipping.txt' in isZip:
                        result.append({'name': i, 'progress': '학습 완료'})
                    else:
                        result.append({'name': i, 'progress': '결과 압축 중'})
                elif i in modelList:
                    if 'error.txt' in os.listdir(os.path.join(modelPath, i)):
                        result.append({'name': i, 'progress': '에러 발생'})
                    else:
                        result.append({'name': i, 'progress': '학습 중'})
                else:
                    result.append({'name': i, 'progress': '학습 요청 대기'})
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
            data = request.get_json()

            result = train.delay(data['proj'], data['images'])

            return {'success': True, 'msg': '학습 요청을 완료했습니다.', 'job_id': str(result)}
        except Exception as e:
            return {'success': False, 'error': e}

@app.route('/api/download/<filename>', methods=['GET'])
def downloadModel(filename):
    if request.method == 'GET':
        try:
            print(request.args, 'args')
            projectName = filename
            modelPath = './models/{}'.format(projectName)
            downloadPath = './output/{}'.format(projectName)

            return send_file(os.path.join(downloadPath, 'output.zip'), mimetype='application/zip', as_attachment=True, attachment_filename='output.zip')
        except Exception as e:
            return {'success': False, 'error': e}

@app.route('/api/delete/<filename>', methods=['POST'])
def deleteModel(filename):
    if request.method == 'POST':
        try:
            shutil.rmtree('./db/{}'.format(filename))
            shutil.rmtree('./models/{}'.format(filename))
            shutil.rmtree('./output/{}'.format(filename))

            return {'success': True, 'msg': '{} 프로젝트의 모델을 삭제했습니다.'.format(filename)}
        except Exception as e:
            print(e)
            return {'success': False, 'error': e}

@app.route('/api/inference', methods=['POST'])
def getImage():
    if request.method == 'POST':
        try:
            reqData = json.loads(request.get_data())

            # base64 버전
            # data = reqData['file'].decode('utf-8').replace('data:image/png;base64,', '')
            # print(data)
            data = base64.b64decode(reqData['file'])

            model = reqData['model']

            # blob 버전
            # data = request.files['file'].read()

            # model = request.form.get('model')
            # print(model)

            predict = inference.run_inference_on_image(data, model)
            
            result = parsePredict(predict['classes'], predict['scores'], 0.3)

            return {'success': True, 'msg': '이미지를 정상적으로 분류하였습니다.', 'predict': result}
        except Exception as e:
            return {'success': False, 'msg': '추론도중 에러가 발생했습니다.', 'error': e}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
