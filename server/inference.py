# -*- coding: utf-8 -*-

"""Inception v3 architecture 모델을 retraining한 모델을 이용해서 이미지에 대한 추론(inference)을 진행하는 예제"""

import numpy as np
import tensorflow.compat.v1 as tf
import re

baseModel = './models/imagenet/classify_image_graph_def.pb'                      # 읽어들일 graph 파일 경로
baseLabel = './models/imagenet/imagenet_synset_to_human_label_map.txt'                   # 읽어들일 labels 파일 경로

class NodeLookup(object):
  def __init__(self,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = './models/imagenet/imagenet_2012_challenge_label_map_proto.pbtxt'
    if not uid_lookup_path:
      uid_lookup_path = './models/imagenet/imagenet_synset_to_human_label_map.txt'
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    """각각의 softmax node에 대해 인간이 읽을 수 있는 영어 단어를 로드 함.
    Args:
      label_lookup_path: 정수 node ID에 대한 문자 UID.
      uid_lookup_path: 인간이 읽을 수 있는 문자에 대한 문자 UID.
    Returns:
      정수 node ID로부터 인간이 읽을 수 있는 문자에 대한 dict.
    """
    if not tf.gfile.Exists(uid_lookup_path):
      tf.logging.fatal('File does not exist %s', uid_lookup_path)
    if not tf.gfile.Exists(label_lookup_path):
      tf.logging.fatal('File does not exist %s', label_lookup_path)

    #  문자 UID로부터 인간이 읽을 수 있는 문자로의 맵핑을 로드함.
    proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # 문자 UID로부터 정수 node ID에 대한 맵핑을 로드함.
    node_id_to_uid = {}
    proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # 마지막으로 정수 node ID로부터 인간이 읽을 수 있는 문자로의 맵핑을 로드함.
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        tf.logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]

def create_graph(model=baseModel):
    """저장된(saved) GraphDef 파일로부터 graph를 생성하고 saver를 반환한다."""
    # 저장된(saved) graph_def.pb로부터 graph를 생성한다.
    with tf.gfile.FastGFile(model, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')

def run_inference_on_image(imageBinary, model=baseLabel):
    image_data = imageBinary
    print(model, 'inference')
    
    labelsFullPath = ''
    modelsFullPath = ''

    if model == 'base':
      labelsFullPath = baseLabel
      modelsFullPath = baseModel
    else:
      labelsFullPath = './models/{}/output_labels.txt'.format(model)
      modelsFullPath = './models/{}/output_graph.pb'.format(model)

    create_graph(modelsFullPath)

    with tf.Session() as sess:
        print(sess.graph)
        # softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
        predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
        predictions = np.squeeze(predictions)

        print('node_lookup')
        node_lookup = NodeLookup()

        top_k = predictions.argsort()[-5:][::-1] 
        print(top_k, '리스트')
        f = open(labelsFullPath, 'rb')
        lines = f.readlines()
        labels = [str(w).replace("\\n", "").replace('b\'', '').replace('\'', '') for w in lines]
        classes = []
        scores = []

        print(classes, 'classes')

        for node_id in top_k:
            classes.append(node_lookup.id_to_string(node_id))
            scores.append(predictions[node_id])
        
        print(classes)

        sess.close()

        return {"classes": classes, "scores": scores}