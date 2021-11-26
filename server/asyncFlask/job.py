# -*- coding: utf-8 -*-

from celery import Celery
import shlex
import subprocess
import redis
import retrain_inceptionV3 as retrain
import os
import shutil
import json
from datetime import datetime

BROKER_URL = 'redis://daein_redis/0'
CELERY_RESULT_BACKEND = 'redis://daein_redis/0'

app = Celery('job', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
rd = redis.StrictRedis(host='redis', port=6379, db=0)

def restartCelery():
    cmd = 'pkill -9 celery'
    subprocess.call(shlex.split(cmd))
    cmd = 'celery multi start -A job worker --loglevel=debug --logfile="./%n%I.log" --pidfile="./%n.pid" --autoscale=2,1 --max-tasks-per-child=1'
    subprocess.call(shlex.split(cmd))

def zipOutput(directoryName):
    try:
        modelPath = '../models/{}'.format(directoryName)
        downloadPath = '../output/{}'.format(directoryName)

        print(modelPath, downloadPath, 'test')

        if not directoryName in os.listdir('../output'):
            progressFilePath = os.path.join(downloadPath, 'zipping.txt')
            os.mkdir(downloadPath)
            f = open(progressFilePath, 'w')
            f.close()
            shutil.make_archive(os.path.join(downloadPath, 'output'), 'zip', modelPath)

        os.remove(progressFilePath)
    except Exception as e:
        print(e)
        f = open(os.path.join(modelPath, 'error.txt'), 'w')
        f.close()

@app.task(name="train", bind=True, max_retries=5, soft_time_limit=600)
def train(self, imagePath):
    try:
        result = retrain.startTrain(imagePath)

        directoryName = imagePath.split('/')[2]

        zipOutput(directoryName)

        create_time = os.path.getctime(f'../models/{directoryName}/output_graph.pb')
        create_timestamp = datetime.fromtimestamp(create_time)

        dbPath = '../db/{}'.format(directoryName)

        downloadPath = '../output/{}'.format(directoryName)

        train_request_id = train.request.id

        dbPath_class = os.listdir(dbPath)

        train_information = {}

        train_information[train_request_id]={}

        train_information[train_request_id]['createtime']=f'{create_timestamp}'

        train_information[train_request_id]['modelName']=directoryName

        train_information[train_request_id]['info']={}

        train_information[train_request_id]['info']['modelPath']=downloadPath

        train_information[train_request_id]['info']['classes']=dbPath_class

        train_information[train_request_id]['info']['images']={}

        for i in dbPath_class:
            dbfile = os.listdir(f'{dbPath}/{i}')
            A = []
            for j in dbfile:
                A.append(f'{dbPath}/{i}/{j}')
            train_information[train_request_id]["info"]["images"][i]=A

        rd.set("train_information", json.dumps(train_information))

        train_information_rd_get=json.loads(rd.get("train_information"))

        return {'success': True}
    except Exception as e:
        self.retry(countdown=5, exc=e)
        f = open(os.path.join('../models', directoryName, 'error.txt'), 'w')
        f.close()
        return {'success': False, 'error': e}