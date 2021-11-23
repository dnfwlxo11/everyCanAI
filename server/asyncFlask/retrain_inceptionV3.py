# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
from datetime import datetime
import hashlib
import os.path
import random
import re
import struct
import sys
import tarfile

import numpy as np
from six.moves import urllib
import tensorflow.compat.v1 as tf

from tensorflow.python.framework import graph_util
from tensorflow.python.framework import tensor_shape
from tensorflow.python.platform import gfile
from tensorflow.python.util import compat

FLAGS = {}

DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
BOTTLENECK_TENSOR_NAME = 'pool_3/_reshape:0'
BOTTLENECK_TENSOR_SIZE = 2048
MODEL_INPUT_WIDTH = 299
MODEL_INPUT_HEIGHT = 299
MODEL_INPUT_DEPTH = 3
JPEG_DATA_TENSOR_NAME = 'DecodeJpeg/contents:0'
RESIZED_INPUT_TENSOR_NAME = 'ResizeBilinear:0'
MAX_NUM_IMAGES_PER_CLASS = 2 ** 27 - 1  # ~134M

def create_image_lists(image_dir, testing_percentage, validation_percentage):
  if not gfile.Exists(image_dir):
    print("Image directory '" + image_dir + "' not found.")
    return None
  result = {}
  sub_dirs = [x[0] for x in gfile.Walk(image_dir)]
  # root directory는 처음에 온다. 따라서 이를 skip한다.
  is_root_dir = True
  for sub_dir in sub_dirs:
    if is_root_dir:
      is_root_dir = False
      continue
    extensions = ['jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG']
    file_list = []
    dir_name = os.path.basename(sub_dir)
    if dir_name == image_dir:
      continue
    print("Looking for images in '" + dir_name + "'")
    for extension in extensions:
      file_glob = os.path.join(image_dir, dir_name, '*.' + extension)
      file_list.extend(gfile.Glob(file_glob))
    if not file_list:
      print('No files found')
      continue
    if len(file_list) < 20:
      print('WARNING: Folder has less than 20 images, which may cause issues.')
    elif len(file_list) > MAX_NUM_IMAGES_PER_CLASS:
      print('WARNING: Folder {} has more than {} images. Some images will '
            'never be selected.'.format(dir_name, MAX_NUM_IMAGES_PER_CLASS))
    label_name = re.sub(r'[^a-z0-9]+', ' ', dir_name.lower())
    training_images = []
    testing_images = []
    validation_images = []
    for file_name in file_list:
      base_name = os.path.basename(file_name)
      hash_name = re.sub(r'_nohash_.*$', '', file_name)
      hash_name_hashed = hashlib.sha1(compat.as_bytes(hash_name)).hexdigest()
      percentage_hash = ((int(hash_name_hashed, 16) %
                          (MAX_NUM_IMAGES_PER_CLASS + 1)) *
                         (100.0 / MAX_NUM_IMAGES_PER_CLASS))
      if percentage_hash < validation_percentage:
        validation_images.append(base_name)
      elif percentage_hash < (testing_percentage + validation_percentage):
        testing_images.append(base_name)
      else:
        training_images.append(base_name)
    result[label_name] = {
        'dir': dir_name,
        'training': training_images,
        'testing': testing_images,
        'validation': validation_images,
    }
  return result


def get_image_path(image_lists, label_name, index, image_dir, category):
  if label_name not in image_lists:
    tf.logging.fatal('Label does not exist %s.', label_name)
  label_lists = image_lists[label_name]
  if category not in label_lists:
    tf.logging.fatal('Category does not exist %s.', category)
  category_list = label_lists[category]
  if not category_list:
    tf.logging.fatal('Label %s has no images in the category %s.',
                     label_name, category)
  mod_index = index % len(category_list)
  base_name = category_list[mod_index]
  sub_dir = label_lists['dir']
  full_path = os.path.join(image_dir, sub_dir, base_name)
  return full_path


def get_bottleneck_path(image_lists, label_name, index, bottleneck_dir, category):
  return get_image_path(image_lists, label_name, index, bottleneck_dir, category) + '.txt'


def create_inception_graph():
  with tf.Graph().as_default() as graph:
    model_filename = os.path.join(
        FLAGS['model_dir'], 'classify_image_graph_def.pb')
    with gfile.FastGFile(model_filename, 'rb') as f:
      graph_def = tf.GraphDef()
      graph_def.ParseFromString(f.read())
      bottleneck_tensor, jpeg_data_tensor, resized_input_tensor = (
          tf.import_graph_def(graph_def, name='', return_elements=[
              BOTTLENECK_TENSOR_NAME, JPEG_DATA_TENSOR_NAME,
              RESIZED_INPUT_TENSOR_NAME]))
  return graph, bottleneck_tensor, jpeg_data_tensor, resized_input_tensor


def run_bottleneck_on_image(sess, image_data, image_data_tensor, bottleneck_tensor):
  bottleneck_values = sess.run(
      bottleneck_tensor,
      {image_data_tensor: image_data})
  bottleneck_values = np.squeeze(bottleneck_values)
  return bottleneck_values


def maybe_download_and_extract():
  dest_directory = FLAGS['model_dir']
  if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)
  filename = DATA_URL.split('/')[-1]
  filepath = os.path.join(dest_directory, filename)
  if not os.path.exists(filepath):

    def _progress(count, block_size, total_size):
      sys.stdout.write('\r>> Downloading %s %.1f%%' %
                       (filename,
                        float(count * block_size) / float(total_size) * 100.0))
      sys.stdout.flush()

    filepath, _ = urllib.request.urlretrieve(DATA_URL,
                                             filepath,
                                             _progress)
    print()
    statinfo = os.stat(filepath)
    print('Successfully downloaded', filename, statinfo.st_size, 'bytes.')
  tarfile.open(filepath, 'r:gz').extractall(dest_directory)


def ensure_dir_exists(dir_name):
  if not os.path.exists(dir_name):
    os.makedirs(dir_name)


def write_list_of_floats_to_file(list_of_floats, file_path):
  s = struct.pack('d' * BOTTLENECK_TENSOR_SIZE, *list_of_floats)
  with open(file_path, 'wb') as f:
    f.write(s)


def read_list_of_floats_from_file(file_path):
  with open(file_path, 'rb') as f:
    s = struct.unpack('d' * BOTTLENECK_TENSOR_SIZE, f.read())
    return list(s)


bottleneck_path_2_bottleneck_values = {}


def create_bottleneck_file(bottleneck_path, image_lists, label_name, index,
                           image_dir, category, sess, jpeg_data_tensor,
                           bottleneck_tensor):
  """Create a single bottleneck file."""
  print('Creating bottleneck at ' + bottleneck_path)
  image_path = get_image_path(image_lists, label_name, index,
                              image_dir, category)
  if not gfile.Exists(image_path):
    tf.logging.fatal('File does not exist %s', image_path)
  image_data = gfile.FastGFile(image_path, 'rb').read()
  try:
    bottleneck_values = run_bottleneck_on_image(
        sess, image_data, jpeg_data_tensor, bottleneck_tensor)
  except:
    raise RuntimeError('Error during processing file %s' % image_path)

  bottleneck_string = ','.join(str(x) for x in bottleneck_values)
  with open(bottleneck_path, 'w') as bottleneck_file:
    bottleneck_file.write(bottleneck_string)


def get_or_create_bottleneck(sess, image_lists, label_name, index, image_dir,
                             category, bottleneck_dir, jpeg_data_tensor,
                             bottleneck_tensor):
  label_lists = image_lists[label_name]
  sub_dir = label_lists['dir']
  sub_dir_path = os.path.join(bottleneck_dir, sub_dir)
  ensure_dir_exists(sub_dir_path)
  bottleneck_path = get_bottleneck_path(image_lists, label_name, index,
                                        bottleneck_dir, category)
  if not os.path.exists(bottleneck_path):
    create_bottleneck_file(bottleneck_path, image_lists, label_name, index,
                           image_dir, category, sess, jpeg_data_tensor,
                           bottleneck_tensor)
  with open(bottleneck_path, 'r') as bottleneck_file:
    bottleneck_string = bottleneck_file.read()
  did_hit_error = False
  try:
    bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
  except ValueError:
    print('Invalid float found, recreating bottleneck')
    did_hit_error = True
  if did_hit_error:
    create_bottleneck_file(bottleneck_path, image_lists, label_name, index,
                           image_dir, category, sess, jpeg_data_tensor,
                           bottleneck_tensor)
    with open(bottleneck_path, 'r') as bottleneck_file:
      bottleneck_string = bottleneck_file.read()
    # Allow exceptions to propagate here, since they shouldn't happen after a
    # fresh creation
    bottleneck_values = [float(x) for x in bottleneck_string.split(',')]
  return bottleneck_values


def cache_bottlenecks(sess, image_lists, image_dir, bottleneck_dir, jpeg_data_tensor, bottleneck_tensor):
  how_many_bottlenecks = 0
  ensure_dir_exists(bottleneck_dir)
  for label_name, label_lists in image_lists.items():
    for category in ['training', 'testing', 'validation']:
      category_list = label_lists[category]
      for index, unused_base_name in enumerate(category_list):
        get_or_create_bottleneck(sess, image_lists, label_name, index,
                                 image_dir, category, bottleneck_dir,
                                 jpeg_data_tensor, bottleneck_tensor)

        how_many_bottlenecks += 1
        if how_many_bottlenecks % 100 == 0:
          print(str(how_many_bottlenecks) + ' bottleneck files created.')


def get_random_cached_bottlenecks(sess, image_lists, how_many, category, bottleneck_dir, image_dir, jpeg_data_tensor, bottleneck_tensor):
  class_count = len(image_lists.keys())
  bottlenecks = []
  ground_truths = []
  filenames = []
  if how_many >= 0:
    # Retrieve a random sample of bottlenecks.
    for unused_i in range(how_many):
      label_index = random.randrange(class_count)
      label_name = list(image_lists.keys())[label_index]
      image_index = random.randrange(MAX_NUM_IMAGES_PER_CLASS + 1)
      image_name = get_image_path(image_lists, label_name, image_index,
                                  image_dir, category)
      bottleneck = get_or_create_bottleneck(sess, image_lists, label_name,
                                            image_index, image_dir, category,
                                            bottleneck_dir, jpeg_data_tensor,
                                            bottleneck_tensor)
      ground_truth = np.zeros(class_count, dtype=np.float32)
      ground_truth[label_index] = 1.0
      bottlenecks.append(bottleneck)
      ground_truths.append(ground_truth)
      filenames.append(image_name)
  else:
    # Retrieve all bottlenecks.
    for label_index, label_name in enumerate(image_lists.keys()):
      for image_index, image_name in enumerate(
          image_lists[label_name][category]):
        image_name = get_image_path(image_lists, label_name, image_index,
                                    image_dir, category)
        bottleneck = get_or_create_bottleneck(sess, image_lists, label_name,
                                              image_index, image_dir, category,
                                              bottleneck_dir, jpeg_data_tensor,
                                              bottleneck_tensor)
        ground_truth = np.zeros(class_count, dtype=np.float32)
        ground_truth[label_index] = 1.0
        bottlenecks.append(bottleneck)
        ground_truths.append(ground_truth)
        filenames.append(image_name)
  return bottlenecks, ground_truths, filenames


def get_random_distorted_bottlenecks(
    sess, image_lists, how_many, category, image_dir, input_jpeg_tensor,
    distorted_image, resized_input_tensor, bottleneck_tensor):
  class_count = len(image_lists.keys())
  bottlenecks = []
  ground_truths = []
  for unused_i in range(how_many):
    label_index = random.randrange(class_count)
    label_name = list(image_lists.keys())[label_index]
    image_index = random.randrange(MAX_NUM_IMAGES_PER_CLASS + 1)
    image_path = get_image_path(image_lists, label_name, image_index, image_dir,
                                category)
    if not gfile.Exists(image_path):
      tf.logging.fatal('File does not exist %s', image_path)
    jpeg_data = gfile.FastGFile(image_path, 'rb').read()
    # Note that we materialize the distorted_image_data as a numpy array before
    # sending running inference on the image. This involves 2 memory copies and
    # might be optimized in other implementations.
    distorted_image_data = sess.run(distorted_image,
                                    {input_jpeg_tensor: jpeg_data})
    bottleneck = run_bottleneck_on_image(sess, distorted_image_data,
                                         resized_input_tensor,
                                         bottleneck_tensor)
    ground_truth = np.zeros(class_count, dtype=np.float32)
    ground_truth[label_index] = 1.0
    bottlenecks.append(bottleneck)
    ground_truths.append(ground_truth)
  return bottlenecks, ground_truths


def should_distort_images(flip_left_right, random_crop, random_scale,
                          random_brightness):
  return (flip_left_right or (random_crop != 0) or (random_scale != 0) or
          (random_brightness != 0))


def add_input_distortions(flip_left_right, random_crop, random_scale,
                          random_brightness):
  jpeg_data = tf.placeholder(tf.string, name='DistortJPGInput')
  decoded_image = tf.image.decode_jpeg(jpeg_data, channels=MODEL_INPUT_DEPTH)
  decoded_image_as_float = tf.cast(decoded_image, dtype=tf.float32)
  decoded_image_4d = tf.expand_dims(decoded_image_as_float, 0)
  margin_scale = 1.0 + (random_crop / 100.0)
  resize_scale = 1.0 + (random_scale / 100.0)
  margin_scale_value = tf.constant(margin_scale)
  resize_scale_value = tf.random_uniform(tensor_shape.scalar(),
                                         minval=1.0,
                                         maxval=resize_scale)
  scale_value = tf.multiply(margin_scale_value, resize_scale_value)
  precrop_width = tf.multiply(scale_value, MODEL_INPUT_WIDTH)
  precrop_height = tf.multiply(scale_value, MODEL_INPUT_HEIGHT)
  precrop_shape = tf.stack([precrop_height, precrop_width])
  precrop_shape_as_int = tf.cast(precrop_shape, dtype=tf.int32)
  precropped_image = tf.image.resize_bilinear(decoded_image_4d,
                                              precrop_shape_as_int)
  precropped_image_3d = tf.squeeze(precropped_image, squeeze_dims=[0])
  cropped_image = tf.random_crop(precropped_image_3d,
                                 [MODEL_INPUT_HEIGHT, MODEL_INPUT_WIDTH,
                                  MODEL_INPUT_DEPTH])
  if flip_left_right:
    flipped_image = tf.image.random_flip_left_right(cropped_image)
  else:
    flipped_image = cropped_image
  brightness_min = 1.0 - (random_brightness / 100.0)
  brightness_max = 1.0 + (random_brightness / 100.0)
  brightness_value = tf.random_uniform(tensor_shape.scalar(),
                                       minval=brightness_min,
                                       maxval=brightness_max)
  brightened_image = tf.multiply(flipped_image, brightness_value)
  distort_result = tf.expand_dims(brightened_image, 0, name='DistortResult')
  return jpeg_data, distort_result


def variable_summaries(var):
  """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
  with tf.name_scope('summaries'):
    mean = tf.reduce_mean(var)
    tf.summary.scalar('mean', mean)
    with tf.name_scope('stddev'):
      stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
    tf.summary.scalar('stddev', stddev)
    tf.summary.scalar('max', tf.reduce_max(var))
    tf.summary.scalar('min', tf.reduce_min(var))
    tf.summary.histogram('histogram', var)


def add_final_training_ops(class_count, final_tensor_name, bottleneck_tensor):
  with tf.name_scope('input'):
    bottleneck_input = tf.placeholder_with_default(
        bottleneck_tensor, shape=[None, BOTTLENECK_TENSOR_SIZE],
        name='BottleneckInputPlaceholder')

    ground_truth_input = tf.placeholder(tf.float32,
                                        [None, class_count],
                                        name='GroundTruthInput')

  # Organizing the following ops as `final_training_ops` so they're easier
  # to see in TensorBoard
  layer_name = 'final_training_ops'
  with tf.name_scope(layer_name):
    with tf.name_scope('weights'):
      initial_value = tf.truncated_normal([BOTTLENECK_TENSOR_SIZE, class_count],
                                          stddev=0.001)

      layer_weights = tf.Variable(initial_value, name='final_weights')

      variable_summaries(layer_weights)
    with tf.name_scope('biases'):
      layer_biases = tf.Variable(tf.zeros([class_count]), name='final_biases')
      variable_summaries(layer_biases)
    with tf.name_scope('Wx_plus_b'):
      logits = tf.matmul(bottleneck_input, layer_weights) + layer_biases
      tf.summary.histogram('pre_activations', logits)

  final_tensor = tf.nn.softmax(logits, name=final_tensor_name)
  tf.summary.histogram('activations', final_tensor)

  with tf.name_scope('cross_entropy'):
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
        labels=ground_truth_input, logits=logits)
    with tf.name_scope('total'):
      cross_entropy_mean = tf.reduce_mean(cross_entropy)
  tf.summary.scalar('cross_entropy', cross_entropy_mean)

  with tf.name_scope('train'):
    optimizer = tf.train.GradientDescentOptimizer(FLAGS['learning_rate'])
    train_step = optimizer.minimize(cross_entropy_mean)

  return (train_step, cross_entropy_mean, bottleneck_input, ground_truth_input,
          final_tensor)


def add_evaluation_step(result_tensor, ground_truth_tensor):
  with tf.name_scope('accuracy'):
    with tf.name_scope('correct_prediction'):
      prediction = tf.argmax(result_tensor, 1)
      correct_prediction = tf.equal(
          prediction, tf.argmax(ground_truth_tensor, 1))
    with tf.name_scope('accuracy'):
      evaluation_step = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  tf.summary.scalar('accuracy', evaluation_step)
  return evaluation_step, prediction


def main():
  try:
    print(FLAGS)

    # TensorBoard의 summaries를 write할 directory를 설정한다.
    if tf.gfile.Exists(FLAGS['summaries_dir']):
      tf.gfile.DeleteRecursively(FLAGS['summaries_dir'])
    tf.gfile.MakeDirs(FLAGS['summaries_dir'])

    # pre-trained graph를 생성한다.
    maybe_download_and_extract()
    graph, bottleneck_tensor, jpeg_data_tensor, resized_image_tensor = (
        create_inception_graph())

    # 폴더 구조를 살펴보고, 모든 이미지에 대한 lists를 생성한다.
    image_lists = create_image_lists(FLAGS['image_dir'], FLAGS['testing_percentage'],
                                    FLAGS['validation_percentage'])
    class_count = len(image_lists.keys())
    if class_count == 0:
      print('No valid folders of images found at ' + FLAGS['image_dir'])
      return -1
    if class_count == 1:
      print('Only one valid folder of images found at ' + FLAGS['image_dir'] +
            ' - multiple classes are needed for classification.')
      return -1

    # 커맨드라인 flag에 distortion에 관련된 설정이 있으면 distortion들을 적용한다.
    do_distort_images = should_distort_images(
        FLAGS['flip_left_right'], FLAGS['random_crop'], FLAGS['random_scale'],
        FLAGS['random_brightness'])

    with tf.Session(graph=graph) as sess:

      if do_distort_images:
        # 우리는 distortion들을 적용할것이다. 따라서 필요한 연산들(operations)을 설정한다.
        (distorted_jpeg_data_tensor,
        distorted_image_tensor) = add_input_distortions(
            FLAGS['flip_left_right'], FLAGS['random_crop'],
            FLAGS['random_scale'], FLAGS['random_brightness'])
      else:
        # 우리는 계산된 'bottleneck' 이미지 summaries를 가지고 있다. 
        # 이를 disk에 캐싱(caching)할 것이다. 
        cache_bottlenecks(sess, image_lists, FLAGS['image_dir'],
                          FLAGS['bottleneck_dir'], jpeg_data_tensor,
                          bottleneck_tensor)

      # 우리가 학습시킬(training) 새로운 layer를 추가한다.
      (train_step, cross_entropy, bottleneck_input, ground_truth_input,
      final_tensor) = add_final_training_ops(len(image_lists.keys()),
                                              FLAGS['final_tensor_name'],
                                              bottleneck_tensor)

      # 우리의 새로운 layer의 정확도를 평가(evalute)하기 위한 새로운 operation들을 생성한다.
      evaluation_step, prediction = add_evaluation_step(
          final_tensor, ground_truth_input)

      # 모든 summaries를 합치고(merge) summaries_dir에 쓴다.(write)
      merged = tf.summary.merge_all()
      train_writer = tf.summary.FileWriter(FLAGS['summaries_dir'] + '/train',
                                          sess.graph)

      validation_writer = tf.summary.FileWriter(
          FLAGS['summaries_dir'] + '/validation')

      # 우리의 모든 가중치들(weights)과 그들의 초기값들을 설정한다.
      init = tf.global_variables_initializer()
      sess.run(init)

      # 커맨드 라인에서 지정한 횟수만큼 학습을 진행한다.
      for i in range(FLAGS['how_many_training_steps']):
        # bottleneck 값들의 batch를 얻는다. 이는 매번 distortion을 적용하고 계산하거나,
        # disk에 저장된 chache로부터 얻을 수 있다.
        if do_distort_images:
          (train_bottlenecks,
          train_ground_truth) = get_random_distorted_bottlenecks(
              sess, image_lists, FLAGS['train_batch_size'], 'training',
              FLAGS['image_dir'], distorted_jpeg_data_tensor,
              distorted_image_tensor, resized_image_tensor, bottleneck_tensor)
        else:
          (train_bottlenecks,
          train_ground_truth, _) = get_random_cached_bottlenecks(
              sess, image_lists, FLAGS['train_batch_size'], 'training',
              FLAGS['bottleneck_dir'], FLAGS['image_dir'], jpeg_data_tensor,
              bottleneck_tensor)
        # grpah에 bottleneck과 ground truth를 feed하고, training step을 진행한다.
        # TensorBoard를 위한 'merged' op을 이용해서 training summaries을 capture한다.

        train_summary, _ = sess.run(
            [merged, train_step],
            feed_dict={bottleneck_input: train_bottlenecks,
                      ground_truth_input: train_ground_truth})
        train_writer.add_summary(train_summary, i)

        # 일정 step마다 graph의 training이 얼마나 잘 되고 있는지 출력한다.
        is_last_step = (i + 1 == FLAGS['how_many_training_steps'])
        if (i % FLAGS['eval_step_interval']) == 0 or is_last_step:
          train_accuracy, cross_entropy_value = sess.run(
              [evaluation_step, cross_entropy],
              feed_dict={bottleneck_input: train_bottlenecks,
                        ground_truth_input: train_ground_truth})
          print('%s: Step %d: Train accuracy = %.1f%%' % (datetime.now(), i,
                                                          train_accuracy * 100))
          print('%s: Step %d: Cross entropy = %f' % (datetime.now(), i,
                                                    cross_entropy_value))
          validation_bottlenecks, validation_ground_truth, _ = (
              get_random_cached_bottlenecks(
                  sess, image_lists, FLAGS['validation_batch_size'], 'validation',
                  FLAGS['bottleneck_dir'], FLAGS['image_dir'], jpeg_data_tensor,
                  bottleneck_tensor))
          # validation step을 진행한다.
          # TensorBoard를 위한 'merged' op을 이용해서 training summaries을 capture한다.
          validation_summary, validation_accuracy = sess.run(
              [merged, evaluation_step],
              feed_dict={bottleneck_input: validation_bottlenecks,
                        ground_truth_input: validation_ground_truth})
          validation_writer.add_summary(validation_summary, i)
          print('%s: Step %d: Validation accuracy = %.1f%% (N=%d)' %
                (datetime.now(), i, validation_accuracy * 100,
                len(validation_bottlenecks)))

      # 트레이닝 과정이 모두 끝났다.
      # 따라서 이전에 보지 못했던 이미지를 통해 마지막 test 평가(evalution)을 진행한다.
      test_bottlenecks, test_ground_truth, test_filenames = (
          get_random_cached_bottlenecks(sess, image_lists, FLAGS['test_batch_size'],
                                        'testing', FLAGS['bottleneck_dir'],
                                        FLAGS['image_dir'], jpeg_data_tensor,
                                        bottleneck_tensor))
      test_accuracy, predictions = sess.run(
          [evaluation_step, prediction],
          feed_dict={bottleneck_input: test_bottlenecks,
                    ground_truth_input: test_ground_truth})
      print('Final test accuracy = %.1f%% (N=%d)' % (
          test_accuracy * 100, len(test_bottlenecks)))

      if FLAGS['print_misclassified_test_images']:
        print('=== MISCLASSIFIED TEST IMAGES ===')
        for i, test_filename in enumerate(test_filenames):
          if predictions[i] != test_ground_truth[i].argmax():
            print('%70s  %s' % (test_filename,
                                list(image_lists.keys())[predictions[i]]))

      # 학습된 graph와 weights들을 포함한 labels를 쓴다.(write)
      tf.io.write_graph(sess.graph, './models/{}/'.format(FLAGS['model_graphdef']), 'model.graphdef')
      output_graph_def = graph_util.convert_variables_to_constants(
          sess, graph.as_graph_def(), [FLAGS['final_tensor_name']])
      with gfile.FastGFile(FLAGS['output_graph'], 'wb') as f:
        f.write(output_graph_def.SerializeToString())
      with gfile.FastGFile(FLAGS['output_labels'], 'w') as f:
        f.write('\n'.join(image_lists.keys()) + '\n')

      sess.close()

    print('학습 끝 함수')
    return {'success': True, 'msg': '학습이 완료되었습니다.', 'path': '{},{}'.format(FLAGS['output_graph'], FLAGS['output_labels'])}
  except Exception as e:
    print('error', e)
    return {'success': False, 'msg': '학습 중 에러가 발생했습니다.', 'error': e}

def startTrain(imagePath):
  try:
    directoryName = imagePath.split('/')[2]
    print(directoryName)

    if not os.path.exists('../models/{}'.format(directoryName)):
      os.makedirs('../models/{}'.format(directoryName))

    FLAGS['model_graphdef'] = directoryName
    FLAGS['image_dir'] = '../db/{}'.format(directoryName)
    FLAGS['output_graph'] = '../models/{}/output_graph.pb'.format(directoryName)
    FLAGS['output_labels'] = '../models/{}/output_labels.txt'.format(directoryName)
    FLAGS['summaries_dir'] = '../models/{}/retrain_logs'.format(directoryName)
    FLAGS['how_many_training_steps'] = 100
    FLAGS['learning_rate'] = 0.01
    FLAGS['testing_percentage'] = 10
    FLAGS['validation_percentage'] = 10
    FLAGS['eval_percentage'] = 10
    FLAGS['eval_step_interval'] = 10
    FLAGS['train_batch_size'] = 10
    FLAGS['test_batch_size'] = -1
    FLAGS['validation_batch_size'] = 10
    FLAGS['print_misclassified_test_images'] = False
    FLAGS['model_dir'] = '../models/imagenet'
    FLAGS['bottleneck_dir'] = '../models/{}/bottleneck'.format(directoryName)
    FLAGS['final_tensor_name'] = 'final_result'
    FLAGS['flip_left_right'] = False
    FLAGS['random_crop'] = 0
    FLAGS['random_scale'] = 0
    FLAGS['random_brightness'] = 0 

    result = main()

    return result
  except Exception as e:
    print(e)
    f = open(os.path.join('../models', directoryName, 'error.txt'), 'w')
    f.close()