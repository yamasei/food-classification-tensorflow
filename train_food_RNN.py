# -*- coding: UTF-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import itertools

from keras.layers.recurrent import GRU
from keras.optimizers import Adam
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.callbacks import Callback

from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import OneHotEncoder

# Callback class to visialize training progress
class LossHistory(Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'batch':[], 'epoch':[]}
        self.accuracy = {'batch':[], 'epoch':[]}
        self.val_loss = {'batch':[], 'epoch':[]}
        self.val_acc = {'batch':[], 'epoch':[]}

    def on_batch_end(self, batch, logs={}):
        self.losses['batch'].append(logs.get('loss'))
        self.accuracy['batch'].append(logs.get('acc'))
        self.val_loss['batch'].append(logs.get('val_loss'))
        self.val_acc['batch'].append(logs.get('val_acc'))

    def on_epoch_end(self, batch, logs={}):
        self.losses['epoch'].append(logs.get('loss'))
        self.accuracy['epoch'].append(logs.get('acc'))
        self.val_loss['epoch'].append(logs.get('val_loss'))
        self.val_acc['epoch'].append(logs.get('val_acc'))

    def loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))
        plt.figure()
        # acc
        plt.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
        # loss
        plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':
            # val_acc
            plt.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
            # val_loss
            plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        plt.grid(True)
        plt.xlabel(loss_type)
        plt.ylabel('acc-loss')
        plt.legend(loc="upper right")
        plt.show()

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

print('\nCreating dataset...')

X_TRAIN_list = []
Y_TRAIN_list = []
X_TEST_list = []
Y_TEST_list = []

FileNames_train = ["Data/chicken_curry_train.npy", "Data/french_fries_train.npy", 'Data/pizza_train.npy', "Data/macarons_train.npy", "Data/miso_soup_train.npy"]
FileNames_test = ["Data/chicken_curry_test.npy", "Data/french_fries_test.npy", 'Data/pizza_test.npy', "Data/macarons_test.npy", "Data/miso_soup_test.npy"]

target = 0

# reading image
for filename in FileNames_train:
    data = np.load(filename)
    X_TRAIN_list.extend(data)
    Y_TRAIN_list += [target] * data.shape[0]
    target += 1

target = 0
for filename in FileNames_test:
    data = np.load(filename)
    X_TEST_list.extend(data)
    Y_TEST_list  += [target] * data.shape[0]
    target += 1


train_x = X_TRAIN_list
one_hots_train = Y_TRAIN_list
test_x = X_TEST_list
one_hots_test = Y_TEST_list

# processing data
one_hots_train = np.reshape(one_hots_train, (-1, 1))

ohe = OneHotEncoder()
one_hots_train = ohe.fit_transform(one_hots_train).A
one_hots_test = np.reshape(one_hots_test, (-1, 1))
one_hots_test = ohe.fit_transform(one_hots_test).A

p = np.random.permutation(len(train_x))
train_x = np.array(train_x)[p]
one_hots_train = one_hots_train[p]

train_x = train_x.reshape([train_x.shape[0], train_x.shape[1], -1])
test_x = np.array(test_x)
test_x = test_x.reshape([test_x.shape[0], test_x.shape[1], -1])

input_shape = (train_x.shape[1], train_x.shape[2])

print('Build RNN Model:')
model= Sequential()
model.add(GRU(32,input_shape = input_shape,activation = 'relu',return_sequences = False ) )
model.add(Dense(64, init='normal', activation='relu'))
model.add(Dropout(0.3))
# model.add(Dense(128, init='normal', activation='relu'))
# model.add(Dropout(0.3))
# model.add(Dense(32, init='normal', activation='relu'))
# model.add(Dropout(0.3))
model.add(Dense(5, activation='softmax'))

# training
his=LossHistory()

model.compile(loss='mean_squared_error', optimizer=Adam(1e-4), metrics=['accuracy'])

X_train = train_x
Y_train = one_hots_train
X_test = test_x
Y_test = one_hots_test

model.fit(train_x, one_hots_train, batch_size=32, epochs=200, verbose=1, validation_split=0.2, callbacks=[his])

print('Test:')
score, accuracy = model.evaluate(test_x, one_hots_test)

print('Test Score:{:.3}'.format(score))
print('Test accuracy:{:.3}'.format(accuracy))

his.loss_plot('epoch')

Y_pred = model.predict(test_x)

# confusion matrix
plt.figure()
cfm=confusion_matrix(np.argmax(one_hots_test,axis=1),np.argmax(Y_pred,axis=1))
np.set_printoptions(precision=2)
class_names=['chicken curry','french fries', 'pizza', 'macarons', "miso soup"]
plot_confusion_matrix(cfm,classes=class_names,title='Confusion Matrix', normalize=True)
plt.show()