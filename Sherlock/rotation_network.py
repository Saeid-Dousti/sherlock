from __future__ import absolute_import, division, print_function, unicode_literals

import os
import glob
import argparse

import tensorflow as tf 
from tensorflow import keras
from tensorflow.keras.applications import MobileNetV2
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

import numpy as np
from data import build_missouri_dataset
from math import ceil


def parse_args(): 
	desc = "Unsupervised training using image rotations on missouri camera traps dataset" 
	parser = argparse.ArgumentParser(description=desc)

	parser.add_argument('--res', type=int, help='Image Resolution', default=224)
	parser.add_argument('--lr', type=float, help='Learning Rate', default=1e-3)
	parser.add_argument('--batch_size', type=int, help='Batch Size', default=16)
	parser.add_argument('--epochs', type=int, help='Training Epochs', default=30)
	parser.add_argument('--save', help='Save model', action='store_true')

	args = parser.parse_args()
	return args


def main():
	args = parse_args()

	callbacks = None
	if args.save:
		logdir = 'logdir/{}_{:03d}'.format("missouri_camera_traps", len(glob.glob('logdir/*')))
		callbacks = [keras.callbacks.ModelCheckpoint(os.path.join(logdir, 'mobilenetv2.h5')), 
					 keras.callbacks.TensorBoard(log_dir=logdir)]

	ds_train = build_missouri_dataset(split='train', image_shape=(args.res, args.res), rotate=True, batch_size=args.batch_size)
	ds_val = build_missouri_dataset(split='val', image_shape=(args.res, args.res), rotate=True, batch_size=args.batch_size)
	ds_test = build_missouri_dataset(split='test', image_shape=(args.res, args.res), rotate=True, batch_size=args.batch_size)

	model = MobileNetV2(input_shape=(args.res, args.res, 3), classes=4, weights=None)

	model.compile(optimizer=keras.optimizers.Adam(learning_rate=args.lr),
				  loss='sparse_categorical_crossentropy',
				  metrics=['accuracy'])

	model.fit(ds_train, 
			  epochs=args.epochs,
			  steps_per_epoch=ceil(17190/args.batch_size), 
			  callbacks=callbacks,
			  validation_data=ds_val,
			  validation_steps=ceil(3588/args.batch_size),
			  verbose=1)

	model.evaluate(ds_test, callbacks=callbacks)




if __name__ == '__main__':
	main()
