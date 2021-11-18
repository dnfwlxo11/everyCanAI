# -*- coding: utf-8 -*-

from celery import Celery
import redis
import retrain_inceptionV3 as retrain

BROKER_URL = 'redis://daein_redis/0'
CELERY_RESULT_BACKEND = 'redis://daein_redis/0'

app = Celery('job', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
rd = redis.StrictRedis(host='localhost', port=16006, db=0)

@app.task(name="test")
def test(x, y):
    sumi = 0

    for i in range(1, 100000000):
        sumi += (x+y+i)
    
    print(sumi, '완료')
    return sumi

@app.task(name="train")
def train(imagePath):
    try:
        result = retrain.startTrain(imagePath)

        print(train.request.id)

        return {'success': True}
    except Exception as e:
        print(e)
        return {'success': False, 'error': e}