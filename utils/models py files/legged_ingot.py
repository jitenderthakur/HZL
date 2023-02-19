# PyTorch Hub
import torch
import cv2
import glob
import logging as lg
import time
import pandas as pd
from datetime import date
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfFileMerger
import csv
import collections
import fpdf
import sys
import cv2
import os
from uuid import uuid4
import base64

import tensorflow as tf
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import json
import numpy as np
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt

def legged_ingots(img,loaded_model):
	loaded_model.layers[0].input_shape #(None, 200, 200, 3)
	jpg_original=base64.b64decode(img)
	jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
	img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
	img = cv2.resize(img,(200,200),interpolation = cv2.INTER_AREA)
	print(img.shape)
	x = np.expand_dims(img, axis = 0)
	x = x/255
	print(x.shape)
	#images = np.vstack([x])
	result = loaded_model.predict(x)
	if result[0] > 0:
		print('legged ingot not found')
		return 0
	else:
		print('legged ingot found')
		return 1