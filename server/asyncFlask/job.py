# -*- coding: utf-8 -*-

from celery import Celery
import shlex
import subprocess
import redis
import retrain_inceptionV3 as retrain
import os
import shutil

BROKER_URL = 'redis://redis-local/0'
CELERY_RESULT_BACKEND = 'redis://redis-local/0'

app = Celery('job', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
rd = redis.StrictRedis(host='localhost', port=6379, db=0)

def restartCelery():
    cmd = 'pkill -9 celery'
    subprocess.call(shlex.split(cmd))
    cmd = 'celery multi start -A job worker --loglevel=debug --logfile="./%n%I.log" --pidfile="./%n.pid"'
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
        f = open(os.path.join(downloadPath, 'error.txt'), 'w')
        f.close()

@app.task(name="test")
def test(x, y):
    sumi = 0

    for i in range(1, 100000000):
        sumi += (x+y+i)
    
    print(sumi, '완료')
    return sumi

@app.task(name="train", bind=True, max_retries=5, soft_time_limit=600)
def train(self, imagePath):
    try:
        result = retrain.startTrain(imagePath)

        directoryName = imagePath.split('/')[2]

        zipOutput(directoryName)
        print(train.request.id)

        return {'success': True}
    except Exception as e:
        print(e)
        self.retry(countdown=5, exc=e)
        return {'success': False, 'error': e}