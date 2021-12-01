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

BROKER_URL = 'redis://192.168.0.106:16006/0'
CELERY_RESULT_BACKEND = 'redis://192.168.0.106:16006/0'

app = Celery('job', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
rd = redis.StrictRedis(host='192.168.0.106', port=16006, db=0)

def restartCelery():
    cmd = 'pkill -9 celery'
    subprocess.call(shlex.split(cmd))
    cmd = 'celery multi start -A job worker --loglevel=debug --logfile="./%n%I.log" --pidfile="./%n.pid" --autoscale=2,1 --max-tasks-per-child=1'
    subprocess.call(shlex.split(cmd))

def saveTrainImage(proj, images):
    try:
        if not os.path.exists('../db/{}'.format(proj)):
            os.makedirs('../db/{}'.format(proj))
        
        for i in images.keys():
            if not os.path.exists('../db/{}/{}'.format(proj, i)):
                os.makedirs('../db/{}/{}'.format(proj, i))

            for j in images[i]:
                url = 'http://192.168.0.106:16004/images/{}/{}/{}'.format(proj, i, j)
                savePath = '../db/{}/{}/{}'.format(proj, i, j)
                res = requests.get(url)
                image = Image.open(BytesIO(res.content)).convert('RGB')
                image.save(savePath)
    except Exception as e:
        print(e)
        f = open(os.path.join('../db', proj, 'error.txt'), 'w')
        f.close()

def zipOutput(directoryName):
    try:
        modelPath = '../models/{}'.format(directoryName)
        downloadPath = '../output/{}'.format(directoryName)

        progressFilePath = os.path.join(downloadPath, 'zipping.txt')

        if not directoryName in os.listdir('../output'):    
            os.mkdir(downloadPath)
            f = open(progressFilePath, 'w')
            f.close()
            shutil.make_archive(os.path.join(downloadPath, 'output'), 'zip', modelPath)

        os.remove(progressFilePath)
    except Exception as e:
        print(e)
        f = open(os.path.join(modelPath, 'error.txt'), 'w')
        f.close()

@app.task(name="train")
def train(directoryName, imagePath):
    try:
        saveTrainImage(directoryName, imagePath)

        print(directoryName, imagePath)
        result = retrain.startTrain(directoryName)

        zipOutput(directoryName)

        return {'success': True}
    except Exception as e:
        print(e)
        f = open(os.path.join('../models', directoryName, 'error.txt'), 'w')
        f.close()