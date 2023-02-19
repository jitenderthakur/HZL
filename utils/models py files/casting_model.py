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
import json
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
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import json
import numpy as np
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
from pytz import timezone
#logging
logger = lg.basicConfig(filename = "log_files_server/"+"server_logs_"+str(datetime.now().date())+".log", 
                        level = lg.INFO, 
                        format = '%(asctime)s %(message)s',force=True)
algo8_python_logger = lg.getLogger()

def model_process(model,img,count):
#     model_path = '/home/ubuntu/HZL/hzl_pipeline/yolov5/2022_04_08_cam1_big_dross.pt'
#     model = torch.hub.load("/home/ubuntu/HZL/hzl_pipeline/yolov5",
#                             "custom",path = model_path,source = 'local',force_reload=True,)   # or yolov5m, yolov5l, yolov5x, 
    print('model_process')
    algo8_python_logger.info({"message": "casting_model"})
    results1 = model(img)
    algo8_python_logger.info({"message": "model passed over yolov5"})
    bbox_threshold=0.015
    results = results1.pandas().xyxy[0].to_dict(orient="records")
    bbox = json.dumps(results, indent = 4)
    #print(bbox)
    today = date.today()
    day = str(today)
    now = datetime.now()
    current_time = now.strftime("%y_%m_%d_%H_%M_%S")
    curr_time = str(current_time)
    img_name = 'cast_'+curr_time+'_'+str(count)+".jpg"
    curr_time = str(current_time)
    uuid_val = str(uuid4())
    if results:
        cav = 0
        cra = 0
        dro = 0
        fi = 0
        for result in results:
            con = result['confidence']
            cs = result['name']
            x1 = int(result['xmin'])
            y1 = int(result['ymin'])
            x2 = int(result['xmax'])
            y2 = int(result['ymax'])
            area = (x2 - x1) * (y2 - y1)
            algo8_python_logger.info({"message": "area calculated"})
            #print("area:",area)
            img_size=(2048,2448)
            #img_size[1]=2448
            norm_area = area / (img_size[0] * img_size[1])
            algo8_python_logger.info({"message": "norm_area calculated"})
            algo8_python_logger.info({"message": "checking fin condition"})
            try:
                if y1 >= 450 and y2 <= 1785 and x1>240 and x2<2400:
                    print('defected')
                    #logger.info({"message:":'defected Ingot',"time:":t})
                    defect_name = [i['name'] for i in results]
                    # using Counter to find frequency of elements
                    frequency = collections.Counter(defect_name)
                    cavity = frequency['cavity']
                    crack = frequency['crack']
                    dross = frequency['dross']
                    fin = frequency['fin']
                    if cs=="fin":
                        if norm_area > bbox_threshold:
                            fi = fi+fin
                            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 5)
                            text = cs
                            cv2.putText(img, text, (x1+100, y1+40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 6)
                            img_path = '/home/ubuntu/HZL/hzl_pipeline/defected_images/'+img_name
                            cv2.imwrite(img_path,img)
                    else:
                        cav = cav+cavity
                        cra = cra+crack
                        dro = dro + dross
                        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 5)
                        text = cs
                        cv2.putText(img, text, (x1+100, y1+40),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 6)
                        img_path = '/home/ubuntu/HZL/hzl_pipeline/defected_images/'+img_name
                        cv2.imwrite(img_path,img)
            except Exception as e:
                algo8_python_logger.info({"message": e})
        return cav, cra, dro, fi, img_name, uuid_val, now,bbox
    else:
        cav=0
        cra=0
        dro=0
        fi =0
        return cav,cra,dro,fi,img_name,uuid_val,now,bbox
        
        
    

def empty_tray(img, loaded_model):
    loaded_model.layers[0].input_shape
    img = cv2.resize(img, (200, 200), interpolation=cv2.INTER_AREA)
    img = image.img_to_array(img)
    img = img/255
    img = np.expand_dims(img, axis=0)
    print('img_done')
    result = loaded_model.predict(img)
    if result[0] > 0:
        print('Good Tray')
        return False
    else:
        print('Empty Tray')
        return True
