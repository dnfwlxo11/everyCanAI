# -*- coding: utf-8 -*-

"""Inception v3 architecture 모델을 retraining한 모델을 이용해서 이미지에 대한 추론(inference)을 진행하는 예제"""

import numpy as np
import tensorflow.compat.v1 as tf

imagePath = './snack.jpg'                                      # 추론을 진행할 이미지 경로
modelFullPath = './models/output_graph.pb'                      # 읽어들일 graph 파일 경로
labelsFullPath = './models/output_labels.txt'                   # 읽어들일 labels 파일 경로


def create_graph():
    """저장된(saved) GraphDef 파일로부터 graph를 생성하고 saver를 반환한다."""
    # 저장된(saved) graph_def.pb로부터 graph를 생성한다.
    with tf.gfile.FastGFile(modelFullPath, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')

def run_inference_on_image(imageBinary):
    image_data = imageBinary

    create_graph()

    with tf.Session() as sess:
        
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
        predictions = np.squeeze(predictions)
        top_k = predictions.argsort()[-5:][::-1]  
        f = open(labelsFullPath, 'rb')
        lines = f.readlines()
        labels = [str(w).replace("\\n", "").replace('b\'', '').replace('\'', '') for w in lines]
        classes = []
        scores = []
        for node_id in top_k:
            classes.append(labels[node_id])
            scores.append(predictions[node_id])
        
        return {"classes": classes, "scores": scores}