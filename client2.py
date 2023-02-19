#from sap import upload_img_from_fold ,remove_img
from __future__ import print_function
import requests
import json
import cv2
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
import json
import base64
from PIL import Image
from base64 import decodestring
import numpy as np
import sys
import time
import os
import neoapi
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
from legged_ingot import legged_ingots
import tensorflow as tf
import glob
import os.path
from hist_data import get_data
from shift_hzl_time import check_shift
from mail_service import mail_camera_status
import logging as lg
logger = lg.basicConfig(filename = "log_files/"+"Log_stack"+str(datetime.now().date())+".log", 
                        level = lg.INFO, 
                        format = '%(asctime)s %(message)s')
algo8_python_logger = lg.getLogger()
# from flaskext.mysql import MySQL

#start the timer
# ''' start= time.perf_counter()

# # This is the path where all the frames that are not uploaded on SAP will be stored
# files_path='K:/testing'  
path = 'C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\stacking_img\\*'
genericCounter , batch , legged_ingot_count,ingot_count = get_data(path)

now = datetime.now()
hour = datetime.now().strftime('%H:%M')
# url = "https://vsystem.ingress.dh-4oondf7m.dhaas-live.shoot.live.k8s-hana.ondemand.com/app/pipeline-modeler/openapi/service/9e7235a0-6868-484a-bd30-5c6af0fcc43f/v1/uploadjson/"
content_type = 'application/json'
headers = {'content-type' : content_type}

addr = 'http://13.126.123.224:7000'
test_url = addr + '/stacking'

legged_model = tf.keras.models.load_model('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\arresh file\\arresh file\\hzl_leg_ingot_SVM.h5')
# get image and display (opencv)
result = 0
# genericCounter=1
# batch = 0
# legged_ingot_count = 0
frames=0
frame_status=False
prev_shift=''

try:
    camera = neoapi.Cam()
    camera.Connect("192.168.1.23")
    algo8_python_logger.info({"message": "logging camera"})
    # camera.Connect()
    camera.f.ExposureTime.Set(14000)

    save_image = True
    first_event = True
    
    while True:
    #or cnt in range(0, 200):
        img = camera.GetImage();
        if not img.IsEmpty():

            #set frames=0
            frames=0
            # send mail when camera starts working
            if frame_status==True:
                mail_camera_status('stackng camera is now working')
                algo8_python_logger.info({"message": "casting camera is working"})
                frame_status==False

           
            # print("frame_starting_time:",one_frame_time)
            imgarray = img.GetNPArray()
            algo8_python_logger.info({"message": "getting image_array"})
            #print("imagearray",imgarray.shape)
            jpg_img = cv2.imencode('.jpg', imgarray)[1]
            print(jpg_img.shape)
            #print(img_encoded)
            b64_string = base64.b64encode(jpg_img).decode('utf-8')
            
            title = 'Press [ESC] to exit ..'
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)
            #cv2.imshow(title, imgarray)
            if save_image:
                algo8_python_logger.info({"message": "saving image"})
                now = datetime.now()
                current_hour = datetime.now().hour
                current_time = str(now.strftime("%y_%m_%d_%H_%M_%S"))
                genericCounter+=1
                ingot_count+=1
                legged_ingot_status=legged_ingots(b64_string,legged_model) 
                algo8_python_logger.info({"message": "checked legged ingots "})
                if legged_ingot_status==1:
                    legged_ingot_count+=1
                    
                else:
                    legged_ingot_count = 0
                if legged_ingot_count == 1:
                    batch+=1
                    ingot_count=1
                current_shift = check_shift()
                if first_event == True:
                    print("First event identified!")
                    prev_shift = current_shift
                    first_event = False
                if current_shift != prev_shift:
                    batch =0
                    genericCounter = 0
                    legged_ingot_count = 0
                    prev_shift=current_shift

                cv2.imwrite('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\stacking_img\\stack_'+current_time+'_'+str(genericCounter)+'_'+str(batch)+'_'+str(ingot_count)+".jpg",imgarray)

                #print(cv2.imwrite('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\casting_img\\cast_'+current_time+".jpg",imgarray))
                algo8_python_logger.info({"message": "saving images in casting folder"})
                try:
                    # saving frame on SAP
                    # one_frame_time = time.time()
                    response = requests.post(test_url,data=json.dumps({'genericCounter':str(genericCounter),'batch':str(batch),'legged_ingot_count':str(ingot_count),'legged_ingot_status':str(legged_ingot_status),'image':b64_string}),headers=headers)
                    algo8_python_logger.info({"message": "push image into Flask api"})
                    # elapsed_time_one_frame = round((time.time() - one_frame_time),3)
                    # print("OneFrameTime:",elapsed_time_one_frame)
                    print(response.status_code)
                    if response.status_code !=200:
                        cv2.imwrite('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\failed_stack_img\\stack_'+current_time+'_'+str(genericCounter)+'_'+str(batch)+'_'+str(ingot_count)+".jpg",imgarray)
                except requests.HTTPError as exception:
                    print(exception)
                    algo8_python_logger.info({"error": exception})

        else:
            print('no frame')
            algo8_python_logger.info({"message": "no frame"})
            text='stacking camera is not working'
            # algo8_python_logger.info({"message": "no frame"})
            frames+=1
            # send mail if camera is not working for more then 1hr
            if (frames>21600) and (frame_status==False):
                frame_status=True
                mail_camera_status(text)                 
        
        if cv2.waitKey(1) == 27:
            break
    
    cv2.destroyAllWindows()

except (neoapi.NeoException, Exception) as exc:
    print('error: ', exc)
    algo8_python_logger.info({"error": exc})
    result = 1

sys.exit(result)