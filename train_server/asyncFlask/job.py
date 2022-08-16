# -*- coding: utf-8 -*-

from celery import Celery
import shlex
import subprocess
import redis
import retrain_inceptionV3 as retrain
import os
import shutil
from PIL import Image
from io import BytesIO
import requests

BROKER_URL = 'redis://every-redis-db:6379/0'
CELERY_RESULT_BACKEND = 'redis://every-redis-db:6379/0'

app = Celery('job', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
rd = redis.StrictRedis(host='localhost', port=6379, db=0)

def restartCelery():
    cmd = 'pkill -9 celery'
    subprocess.call(shlex.split(cmd))
    cmd = 'celery multi start -A job worker --loglevel=debug --logfile="./%n%I.log" --pidfile="./%n.pid" --autoscale=2,1 --max-tasks-per-child=1'
    subprocess.call(shlex.split(cmd))

def saveTrainImage(proj, images):
    print('사진 다운 시작')
    if not os.path.exists('../db/{}'.format(proj)):
        os.makedirs('../db/{}'.format(proj))
    
    for i in images.keys():
        if not os.path.exists('../db/{}/{}'.format(proj, i)):
            os.makedirs('../db/{}/{}'.format(proj, i))

        for j in images[i]:
            url = 'http://every-app-server:3000/images/{}/{}/{}'.format(proj, i, j)
            savePath = '../db/{}/{}/{}'.format(proj, i, j)
            res = requests.get(url)
            image = Image.open(BytesIO(res.content)).convert('RGB')
            image.save(savePath)

    print('사진 다운 끝')

def zipOutput(directoryName):
    modelPath = '../models/{}'.format(directoryName)
    downloadPath = '../output/{}'.format(directoryName)

    progressFilePath = os.path.join(downloadPath, 'zipping.txt')

    if not directoryName in os.listdir('../output'):    
        os.mkdir(downloadPath)
        f = open(progressFilePath, 'w')
        f.close()
        shutil.make_archive(os.path.join(downloadPath, 'output'), 'zip', modelPath)

    os.remove(progressFilePath)

@app.task(name="train")
def train(directoryName, imagePath):
    print('작업 요청옴')

    saveTrainImage(directoryName, imagePath)

    print(directoryName, imagePath)
    result = retrain.startTrain(directoryName)

    zipOutput(directoryName)

    return {'success': True}