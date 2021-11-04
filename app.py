# -*- coding: utf-8 -*-

import json
from flask import Flask, request
from werkzeug.utils import secure_filename
import inference

app = Flask(__name__)

calorieDBPath = './calorieDB/food_cal.json'

# args : (classes 배열, scores 배열, 원하는 score의 정도
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


@app.route('/', methods=['GET'])
def hello():
    if request.method == 'GET':
        try:
            print('서버가 정상적으로 동작중')

            return {'success': True, 'msg': '플라스크 http 통신 테스트'}
        except Exception as e:
            return {'success': False, 'msg': 'GET 요청 테스트 중 에러가 발생했습니다.', 'error': e}

@app.route('/save', methods=['POST'])
def saveImage():
    if request.method == 'POST':
        try:
            file = request.files['file']
            file.save(secure_filename(file.filename))

            return {'success': True, 'msg': '이미지가 정상적으로 저장 되었습니다.'}
        except Exception as e:
            return {'success': False, 'msg': '이미지 저장 테스트 중 에러가 발생했습니다.', 'error': e}


@app.route('/inference', methods=['POST'])
def getImage():
    if request.method == 'POST':
        try:
            data = request.files['file'].read()
            predict = inference.run_inference_on_image(data)
            result = parseCalorieDB(predict['classes'], predict['scores'], 0.3)

            return {'success': True, 'msg': '이미지를 정상적으로 분류하였습니다.', 'predict': result}
        except Exception as e:
            return {'success': False, 'msg': '추론도중 에러가 발생했습니다.', 'error': e}

if __name__ == '__main__':
    app.run(host='192.168.0.106', port=5000, debug=True)