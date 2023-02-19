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



def stack_stacking_model(model,img,count,img_name):
	# model_path = 'C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\yolov5-master_model2\\yolov5-master\\model2.pt'
	# model = torch.hub.load("C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\yolov5-master_model2\\yolov5-master","custom",path = model_path,source = 'local',force_reload=True,)  # or yolov5m, yolov5l, yolov5x, custom

	contam= 0
	drip_mark= 0
	surface_rough= 0
	water_mark= 0
	hot_cold_shuts=0
	brand_enboss=0
	fi=0

	results1 = model(img)
	results = results1.pandas().xyxy[0].to_dict(orient="records")
	bbox = json.dumps(results, indent = 4)
	print(bbox)
	today = date.today()
	day = str(today)
	now = datetime.now()
	current_time = now.strftime("%y_%m_%d_%H_%M_%S")
	curr_time = str(current_time)
# 	img_name = 'stack_'+curr_time+'_'+str(count)+".jpg"
	curr_time = str(current_time)
	uuid_val = str(uuid4())
	if results:
	    #logger.info({"message:":'defected Ingot',"time:":t})
	    defect_name=[i['name'] for i in results]
	    # using Counter to find frequency of elements
	    frequency = collections.Counter(defect_name)
	    contamination= frequency['contamination']
	    dripping_mark= frequency['dripping_mark']
	    surface_roughness= frequency['surface_roughness']
	    water_marking= frequency['water_marking']
	    hot_and_cold_shuts= frequency['hot_and_cold_shuts']
	    brand_enbossing= frequency['brand_enbossing']
	    fin= frequency['fin']

	    contam= contam + contamination
	    drip_mark= drip_mark + dripping_mark
	    surface_rough= surface_rough + surface_roughness
	    water_mark= water_mark + water_marking
	    hot_cold_shuts= hot_cold_shuts + hot_and_cold_shuts
	    brand_enboss= brand_enboss + brand_enbossing
	    fi= fi+fin
	    
	    for result in results: 
	        con = result['confidence']
	        cs = result['name']  
	        x1 = int(result['xmin'])
	        y1 = int(result['ymin'])
	        x2 = int(result['xmax'])
	        y2 = int(result['ymax'])
	        # Do whatever you want
	        cv2.rectangle(img, (x1, y1), (x2, y2), (255,0,0), 5)
	        text = "{}: {:.2f}".format(cs, con)
	        cv2.putText(img, text, (x1+100, y1+40), cv2.FONT_HERSHEY_SIMPLEX,2, (255,0,0), 6)
	        #bbox_stacking = [x1,y1,x2,y2]
	        
        	img_path = '/home/ubuntu/HZL/hzl_pipeline/defected_images/'+img_name
        	cv2.imwrite(img_path,img)
	return contam, drip_mark, surface_rough,water_mark,hot_cold_shuts,brand_enboss,fi,uuid_val,now,bbox


def stack_legged_ingots(img,loaded_model):
	loaded_model.layers[0].input_shape #(None, 200, 200, 3)
	img = cv2.resize(img,(200,200),interpolation = cv2.INTER_AREA)
	x = np.expand_dims(img, axis = 0)
	images = np.vstack([x])
	result = loaded_model.predict(images)
	if result[0] > 0:
		print('feed is not available')
		return False
	else:
		print('feed is available')
		return True