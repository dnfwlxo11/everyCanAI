from celery import Celery
import retrain_inceptionV3 as retrain

BROKER_URL = 'redis://localhost:16006/0'
CELERY_RESULT_BACKEND = 'redis://localhost:16006/0'

app = Celery('job', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)

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

        return {'success': True}
    except Exception as e:
        print(e)
        return {'success': False, 'error': e}