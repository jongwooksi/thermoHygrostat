import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"

tf.reset_default_graph()
tf.set_random_seed(777)
np.random.seed(777)

input_col_counter = 5 
output_col_counter = 1 
 
len_sequence = 1
hidden_cell = 30  
hidden_cell2 = 20
forget_bias = 10 
forget_bias2 = 10  
keep_prob = 0.7
keep_prob2 = 0.9

epoch_num =20000        
learning_rate = 0.0001


def lstm_cell():
    cell = tf.contrib.rnn.BasicLSTMCell(num_units=hidden_cell, forget_bias=forget_bias, state_is_tuple=True, activation=tf.nn.relu)
    cell = tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=keep_prob)

    cell2 = tf.contrib.rnn.BasicLSTMCell(num_units=hidden_cell2, forget_bias=forget_bias2, state_is_tuple=True, activation=tf.nn.sigmoid)
    cell = tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=keep_prob2)


    return [cell, cell2]



names = ['1','2', '3','4','5','label']
raw_dataframe = pd.read_csv('data.csv', names=names, encoding='utf-8' ) 
raw_dataframe.info() 

inform = raw_dataframe.values[1:].astype(np.float) 

x = inform[:,:-1] 
y = inform[:,-1:]

dataX = [] 
dataY = [] 
 
for i in range(0, len(y) - len_sequence):
    _x = x[i : i+len_sequence]
    _y = y[i] 
    print(_x, _y)
    dataX.append(_x) 
    dataY.append(_y)
 

train_size = int(len(dataY) * 0.7)

test_size = len(dataY) - train_size

x_train = np.array(dataX[0:train_size])
y_train = np.array(dataY[0:train_size])
 
testX = np.array(dataX[train_size:len(dataX)])
testY = np.array(dataY[train_size:len(dataY)])
 
X = tf.placeholder(tf.float32, [None, len_sequence, input_col_counter])
Y = tf.placeholder(tf.float32, [None, 1])

targets = tf.placeholder(tf.float32, [None, 1])
predictions = tf.placeholder(tf.float32, [None, 1])

cell_m = tf.contrib.rnn.MultiRNNCell(lstm_cell(), state_is_tuple=True)

hypo, _states = tf.nn.dynamic_rnn(cell_m, X, dtype=tf.float32)
hypo = tf.contrib.layers.fully_connected(hypo[:, -1], output_col_counter, activation_fn=tf.identity)
loss = tf.reduce_sum(tf.square(hypo - Y))
optimizer = tf.train.AdamOptimizer(learning_rate)

train = optimizer.minimize(loss)
rmse = tf.reduce_mean(tf.squared_difference(targets, predictions))
 
test_predict = ''        
 
train_error_save = []
test_error_save = []

sess = tf.Session()
sess.run(tf.global_variables_initializer())
 
for epoch in range(epoch_num):
    _, _loss = sess.run([train, loss], feed_dict={X: x_train, Y: y_train})

    if ((epoch+1) % 50 == 0) or (epoch == epoch_num-1): 
        
        train_predict = sess.run(hypo, feed_dict={X: x_train})
        train_error = sess.run(rmse, feed_dict={targets: y_train, predictions: train_predict})
        
        test_predict = sess.run(hypo, feed_dict={X: testX})
        test_error = sess.run(rmse, feed_dict={targets: testY, predictions: test_predict})
        
        train_error_save.append(train_error)
        test_error_save.append(test_error)
        
        print("epoch: {}, train_error(A): {:4f}, test_error(B): {:4f}".format(epoch+1, train_error, test_error))

saver = tf.train.Saver()
saver.save(sess, "./Model/trainedModel" )

countzero = 0
countone= 0


for i, j, x in zip(testY, test_predict,testX):
    print(i, j, x, end=" ")

    if i == 0 and j < 0.5:
        print("success")
        countzero += 1

    elif i == 1 and j > 0.5:
        print("success")
        countone += 1
    else :
        print()

print("accuracy")
print((countzero + countone)/len(testY))
