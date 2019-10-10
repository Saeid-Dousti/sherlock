from __future__ import absolute_import, division, print_function, unicode_literals

import os
import glob
import argparse

import tensorflow as tf 
from tensorflow import keras
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

from data import build_yelp_dataset, build_food101_dataset
from model import build_model


def parse_args(): 
	desc = "Unsupervised training using image rotations on missouri camera traps dataset" 
	parser = argparse.ArgumentParser(description=desc)

	parser.add_argument('--res', type=int, help='Image Resolution', default=224)
	parser.add_argument('--lr', type=float, help='Learning Rate', default=1e-4)
	parser.add_argument('--batch_size', type=int, help='Batch Size', default=16)
	parser.add_argument('--epochs', type=int, help='Training Epochs', default=10)
	parser.add_argument('--model', type=str, help='Path to pretrained model or "imagenet"', default=None)
	parser.add_argument('--save', help='Save model', action='store_true')

	args = parser.parse_args()
	return args


def main():
	args = parse_args()

	callbacks = None
	if args.save:
		logdir = 'logdir/{}_{:03d}'.format("food101", len(glob.glob('logdir/*')))
		print('Saving to {}'.format(logdir))
		save_path = os.path.join(logdir, 'mobilenetv2.h5')
		callbacks = [keras.callbacks.ModelCheckpoint(save_path), 
					 keras.callbacks.TensorBoard(log_dir=logdir)]

	ds_train, info = build_food101_dataset(split='train', image_shape=(args.res, args.res), rotate=True, batch_size=args.batch_size)
	ds_test, info = build_food101_dataset(split='test', image_shape=(args.res, args.res), rotate=True, batch_size=args.batch_size)

	model = build_model(base_weights=args.model, classes=4, input_shape=(args.res, args.res, 3))

	model.compile(optimizer=keras.optimizers.Adam(learning_rate=args.lr),
				  loss='sparse_categorical_crossentropy',
				  metrics=['accuracy'])

	model.fit(ds_train, callbacks=callbacks, epochs=args.epochs, steps_per_epoch=info["length"])

	base_model.save(save_path)


if __name__ == '__main__':
	main()
