import tensorflow as tf
from sklearn import datasets
import numpy as np
import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"
thresh = 0.6

def predict(testX):

    path = './Model/trainedModel.meta'
    saver = tf.train.import_meta_graph(path)

    config=tf.ConfigProto(log_device_placement=True)
    config.gpu_options.allow_growth = True
    sess = tf.Session(config= config)

    saver.restore(sess, tf.train.latest_checkpoint('./Model/'))
    graph = tf.get_default_graph()

    X = graph.get_tensor_by_name("Placeholder:0")
    result = graph.get_tensor_by_name("fully_connected/Identity:0")

    test_predict = sess.run(result , feed_dict={X : testX})

    predictVal = test_predict[0][0]
    print(predictVal)

    if predictVal > thresh :return True 
    else: return False
        

if __name__ == '__main__':
    testX = [[[70.5, 70.3, 71, 70.8,73.4]]]

    print("anomaly") if predict(testX) else print("normal") 