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
import logging as lg
import neoapi
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
from hist_data_casting import get_data
import tensorflow as tf
from empty_tray_model import empty_tray
from shift_hzl_time import check_shift
from mail_service import mail_camera_status
logger = lg.basicConfig(filename = "log_files/"+"Log_casting"+str(datetime.now().date())+".log", 
                        level = lg.INFO, 
                        format = '%(asctime)s %(message)s')
algo8_python_logger = lg.getLogger()
# from flaskext.mysql import MySQL

#start the timer
# ''' start= time.perf_counter()

# # This is the path where all the frames that are not uploaded on SAP will be stored
# files_path='K:/testing'  
path = 'C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\casting_img\\*'
genericCounter = get_data(path)
# url = "https://vsystem.ingress.dh-4oondf7m.dhaas-live.shoot.live.k8s-hana.ondemand.com/app/pipeline-modeler/openapi/service/9e7235a0-6868-484a-bd30-5c6af0fcc43f/v1/uploadjson/"
content_type = 'application/json'
headers = {'content-type' : content_type}

addr = 'http://13.126.123.224:7000'
test_url = addr + '/casting'
result = 0
frames=0
frame_status=False
prev_shift=''
#empty tray model
emptyTray_model = tf.keras.models.load_model('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\arresh file\\arresh file\\model_empty_classifier.h5')


try:
    camera = neoapi.Cam()
    algo8_python_logger.info({"message": "logging camera"})
    camera.Connect("192.168.1.24")
    # camera.Connect()
    camera.f.ExposureTime.Set(90000)

    save_image = True
    first_event=True
    
    while True:
    #or cnt in range(0, 200):
        img = camera.GetImage();
        if not img.IsEmpty():
            frames=0
            # send mail when camera starts working
            if frame_status==True:
                mail_camera_status('casting camera is now working')
                algo8_python_logger.info({"message": "casting camera is working"})
                frame_status==False
           
            imgarray = img.GetNPArray()
            algo8_python_logger.info({"message": "getting image_array"})
            #print("imagearray",imgarray.shape)
            jpg_img = cv2.imencode('.jpg', imgarray)[1]
            #print(img_encoded)
            b64_string = base64.b64encode(jpg_img).decode('utf-8')
            
            title = 'Press [ESC] to exit ..'
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)
            #cv2.imshow(title, imgarray)
            if save_image:
                save_image = True
                algo8_python_logger.info({"message": "saving image"})
                #  empty tray model call
                
                empty_tray_status = empty_tray(b64_string,emptyTray_model)
                print(empty_tray_status)
                algo8_python_logger.info({"message": "checked empty tray "})
                if  empty_tray_status!=True:
                    now = datetime.now()
                    current_hour = datetime.now().hour
                    current_time = str(now.strftime("%y_%m_%d_%H_%M_%S"))
                    genericCounter+=1
                    
                    current_shift = check_shift()
                    print('shift: ',current_shift)
                    if first_event == True:
                        print("First event identified!")
                        prev_shift = current_shift
                        first_event = False
                    if current_shift != prev_shift:
                        genericCounter = 0
                        prev_shift=current_shift

                    cv2.imwrite('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\casting_img\\cast_'+current_time+'_'+str(genericCounter)+".jpg",imgarray)
                    #print(cv2.imwrite('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\casting_img\\cast_'+current_time+".jpg",imgarray))
                    algo8_python_logger.info({"message": "saving images in casting folder"})
                    try:
                        # saving frame on SAP
                        response = requests.post(test_url,data=json.dumps({'count':str(genericCounter),'image':b64_string}),headers=headers)
                        algo8_python_logger.info({"message": "push image into Flask api"})
                        print(response)

                        if response.status_code !=200:
                            cv2.imwrite('C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\failed_cast_img\\cast_'+current_time+'_'+str(genericCounter)+".jpg",imgarray)

                
                    except requests.HTTPError as exception:
                        print(exception)
                        algo8_python_logger.info({"error": exception})

                else:
                    print('empty_tray')        
        else:
            print('no frame')
            algo8_python_logger.info({"message": "no frame"})
            text='casting camera is not working'
            algo8_python_logger.info({"message": "casting camera is not working"})
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