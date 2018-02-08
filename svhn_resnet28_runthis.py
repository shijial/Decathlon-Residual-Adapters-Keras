
# coding: utf-8

# In[63]:

import glob
import numpy as np
import sklearn.metrics as metrics
import os
import math
#from keras.datasets import cifar10
import keras.callbacks as callbacks
import keras.utils.np_utils as kutils
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
#from keras.utils import plot_model
#import pydotplus as pydot
from keras import backend as K
import importlib
import resnet28_RAM as resnet_RAM
importlib.reload(resnet_RAM)


# In[64]:


decathlon_data_folder = "/home/paperspace/nbs/data/"


batch_size = 64
nb_epoch = 10
img_rows, img_cols = 64,64
classes = 10

cwd = os.getcwd()
data_folder = decathlon_data_folder + "/svhn/"

train_datagen = ImageDataGenerator(samplewise_center=True, samplewise_std_normalization=True)
valid_datagen = ImageDataGenerator(samplewise_center=True, samplewise_std_normalization=True)
train_generator = train_datagen.flow_from_directory(data_folder + "train", target_size=(img_rows, img_cols),batch_size=batch_size)
valid_generator = valid_datagen.flow_from_directory(data_folder + "val", target_size=(img_rows, img_cols),batch_size=batch_size)

init_shape = (3,img_rows, img_cols ) if K.image_dim_ordering() == 'th' else (img_rows, img_cols ,3)

model = resnet_RAM.create_resnet_RAM(init_shape, filters=64, factor=1, nb_classes=classes, N=4, verbose=1, learnall = True, name = 'imagenet12')

model.summary()
#plot_model(model, to_file = "ResNet28_RAM.png")


# In[72]:
sgd_opt = optimizers.SGD(lr=0.1, decay=0.0005, momentum=0.0, nesterov=False)

model.compile(loss="categorical_crossentropy", optimizer=sgd_opt, metrics=["acc"])
print("Finished compiling")
print("Allocating GPU memory")

#model.load_weights("imagenet_wrn_28_4_RAM_weights.h5")
#print("Model loaded.")


# In[73]:
train_files = glob.glob(data_folder + "/train/*/*")

train_steps = len(train_files)//batch_size

val_files = glob.glob(data_folder + "/val/*/*")

val_steps = len(val_files)//batch_size

print("TVsteps:", train_steps, val_steps)

filepath = "svhn_resnet_RAM_weights.h5"
csv_logger = callbacks.CSVLogger('training_svhn.log', separator = ',', append = True)
#model.fit_generator(generator.flow(trainX, trainY, batch_size=batch_size), steps_per_epoch=len(trainX) // batch_size + 1, nb_epoch=nb_epoch,callbacks = [callbacks.ModelCheckpoint(filepath, monitor='val_acc', verbose=0, save_best_only=True, save_weights_only=False, mode='auto', period=1)],validation_data=(testX, testY),validation_steps=testX.shape[0] // batch_size,)
#model.fit_generator(train_generator, steps_per_epoch= len(train_generator), validation_data=valid_generator, validation_steps = len(valid_generator), epochs = 5, callbacks = [callbacks.ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)])
model.fit_generator(train_generator, steps_per_epoch=train_steps, validation_steps=val_steps, validation_data=valid_generator, epochs = 30, callbacks = [csv_logger, callbacks.ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)])

