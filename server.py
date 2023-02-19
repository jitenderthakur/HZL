"""
Run a rest API exposing the yolov5s object detection model
"""
import argparse
import io
import datetime
import logging as lg
from datetime import datetime
import pandas as pd
from PIL import Image
from flask import Flask, jsonify
import json
import torch
from flask import Flask, request
from cast_upload_model import cast_model_process,cast_empty_tray
from upload_stack_model import stack_stacking_model , stack_legged_ingots

from casting_model import model_process,empty_tray
from stacking_model import stacking_model
import numpy as np
import cv2
import torch
from sqlalchemy import create_engine
from flaskext.mysql import MySQL
import time
import tensorflow as tf
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.regularizers import l2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
from shift_hzl_time import check_shift
from pytz import timezone
import base64
from sync_uploaded_data import sync

app = Flask(__name__)

#logging
logger = lg.basicConfig(filename = "log_files_server/"+"server_logs_"+str(datetime.now().date())+".log", 
                        level = lg.INFO, 
                        format = '%(asctime)s %(message)s',force=True)
algo8_python_logger = lg.getLogger()





#Connection to DataBase and Engine Created.
try:
    connect_query = "mysql+pymysql://"+'admin'+":"+'Dev123456'+"@"+'hzl.cgwyhisjxon9.ap-south-1.rds.amazonaws.com'+":"+"3306"+"/"+"hzl"
    engine = create_engine(connect_query)
    print(True,engine)
except:
    print(False,engine)    


#YOLOV5 Casting Model Load
casting_model_path = '/home/ubuntu/HZL/hzl_pipeline/yolov5/2022_04_08_cam1_big_dross.pt'
model = torch.hub.load("/home/ubuntu/HZL/hzl_pipeline/yolov5","custom",path = casting_model_path,source = 'local',force_reload=True,)  # or yolov5m, yolov5l, yolov5x, custom
# Yolov5 Stacking Model Load
stacking_model_path = '/home/ubuntu/HZL/hzl_pipeline/yolov5-master_model2/yolov5-master/2022_03_26_cam2_retrained_last.pt'
model2 = torch.hub.load("/home/ubuntu/HZL/hzl_pipeline/yolov5-master_model2/yolov5-master",
                        "custom",path = stacking_model_path,source = 'local',force_reload=True,)  # or yolov5m, yolov5l, yolov5x, custom
#empty tray model
loaded_model = tf.keras.models.load_model('/home/ubuntu/HZL/hzl_pipeline/arresh file/model_empty_classifier.h5')

algo8_python_logger.info({"message": "Solution has started running"})
algo8_python_logger.info({"message": "Casting model Running!!"})
print("code Started")

@app.route('/casting', methods=["POST"])
def predict():
    time_infer = time.time()
    if request.method =="POST":
        defected_Y_N = 'N'
        r=request
        count= r.json['count']
        img= r.json['image']
        jpg_original=base64.b64decode(img)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
        print(img.shape)
        algo8_python_logger.info({"message": img.shape})
        algo8_python_logger.info({"message": "Casting Frames Received"})
   
        algo8_python_logger.info({"message": "Casting frames process into yolov5 model"})
        #Yolov5 casting model call
        

        algo8_python_logger.info({"time taken to get one inference in yolov5 model": time.time()-time_infer})
        
        # Yolov5 empty tray model call
        empty_tray_status = empty_tray(img,loaded_model)
        algo8_python_logger.info({"message": "Casting frames process into empty_tray model"})
        #Shift Changes
        shift= check_shift()
        cav,cra,dro,fi,img_name,uuid_val,now, bbox = model_process(model,img,count)
        print("yolov5 Model")
        if cav+cra+dro+fi > 0:
            defected_Y_N = 'Y'
        else:
            defected_Y_N = 'N'
        #Create a DataFrame to take all values and push in to DB.
        df = pd.DataFrame([{'timestamp':now,'imagePath':'NAN','imageName':img_name,'colourTrayStatus':0,
                            'batch':0,'ingotCounter': count,'defected_Y_N':defected_Y_N,'crack':cra, 'cavity':cav,
                            'dross':dro,'fin':fi,'shift':shift,'line':'Hydro 2 Line 1','section':'casting',
                            'weight':25,'supervisor':'Manoj Jain','operatorId':1 ,'resolved_Y_N':'N',
                            'uuid':uuid_val,'defectedType':'NAN','emptyTray': empty_tray_status,'operatorName':'Operator A','boundingBox':bbox}])
        #Push data into DB.
        #print(df)
        df.to_sql("casting",engine,if_exists = "append",index = False)
        #print(df)
        algo8_python_logger.info({"message": "Casting Data Push Successfully INTO DB"})
        algo8_python_logger.info({"time taken to get one complete inference": time.time()-time_infer})
       
    return {'cav':cav,'cra':cra,'dro':dro}

algo8_python_logger.info({"message": "Stacking model Running!!"})
@app.route('/stacking', methods=["POST"])
def predict_stack():
    time_infer = time.time()
    if request.method =="POST":
        defected_Y_N = 'N'
        r=request
        count= r.json['genericCounter']
        batch= r.json['batch']
        legged_ingot_count = r.json['legged_ingot_count']
        legged_ingot_status = r.json['legged_ingot_status']
        algo8_python_logger.info({"legged_ingot_status": legged_ingot_status})
        img= r.json['image']
        jpg_original=base64.b64decode(img)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
        print(img.shape)
        
        algo8_python_logger.info({"message": "Stacking Frames Received"})

        algo8_python_logger.info({"message": "stacking frames process into yolov5 model"})
        #Yolov5 stacking model call
        contam,drip_mark,surface_rough,water_mark,hot_cold_shuts,brand_enboss,fi,img_name,uuid_val,now,bbox= stacking_model(model2,img,count)
        
        if contam+drip_mark+surface_rough+water_mark+hot_cold_shuts+brand_enboss+fi > 0:
            defected_Y_N = 'Y'
        else:
            defected_Y_N = 'N'            

        shift= check_shift()
        algo8_python_logger.info({"message": "stacking frames process into legged_ingots model"})
        #Create a DataFrame to take all values and push in to DB.
        df = pd.DataFrame([{'timestamp':now,'imageName':img_name,'leggedIngotStatus':legged_ingot_status,
                            'batch':batch,'ingotCounter':legged_ingot_count,'defected_Y_N': defected_Y_N,'contamination':contam,
                            'drippingMark':drip_mark, 'surfaceRoughness':surface_rough,
                            'waterMarking':water_mark,'hotAndColdShuts':hot_cold_shuts,
                            'brandEnbossing':brand_enboss,'fin':fi,'spuriousBatchStatus': 'NAN',
                            'shift':shift,'line':'Hydro 2 Line 2','section':'stacking','weight':25,'supervisor':'Manoj Jain',
                            'operatorName':'Operator A' ,'resolved_Y_N':'N','uuid':uuid_val,'imagePath':'NAN','defected':0,'operatorId':1,'boundingBox':bbox,'genericCounter':count}])
        #print(df)
        #Push data into DB.
        df.to_sql("stacking",engine,if_exists = "append",index = False)
        #print(df)
        algo8_python_logger.info({"message": "Stacking Data PUSH Successfully INTO DB"})
    return {'contam':contam,'drip_mark':drip_mark,'surface_rough':surface_rough,'water_mark':water_mark,'hot_cold_shuts':hot_cold_shuts,'brand_enboss':brand_enboss,'fi':fi}

@app.route('/casting_upload', methods=["POST"])
def predict_cast_upload():
    time_infer = time.time()
    if request.method =="POST":
        defected_Y_N = 'N'
        r=request
#         print(r.data)
#         print(r.json)
        
        img= r.json['image']
        timestamp=r.json['timestamp']
        count= r.json['generic_count']
        img_name= r.json['img_name']

        print(count)
        # convert string of image data to uint8
        jpg_original=base64.b64decode(img)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
        print(img.shape)
#         print(count)
        algo8_python_logger.info({"message": "Casting Frames from upload folder Received"})
        algo8_python_logger.info({"timestamp": timestamp,"count":count,"img_name":img_name})
   
        algo8_python_logger.info({"message": "Casting frames process into yolov5 model"})
        #Yolov5 casting model call
        

        algo8_python_logger.info({'count':count,'img_name':img_name})
        
#         Yolov5 empty tray model call
        empty_tray_status = cast_empty_tray(img,loaded_model)
        algo8_python_logger.info({"message": "Casting frames process into empty_tray model"})
        #Shift Changes
        shift= check_shift()
        
        cav, cra, dro, fi, uuid_val,bbox= cast_model_process(model,img,count,img_name)
        if cav+cra+dro+fi > 0:
            defected_Y_N = 'Y'
        else:
            defected_Y_N = 'N'
        print(img_name,cav,cra,dro,fi)
#         Create a DataFrame to take all values and push in to DB.
        try:
            df = pd.DataFrame([{'timestamp':timestamp,'imagePath':'NAN','imageName':img_name,'colourTrayStatus':0,
                                'batch':0,'ingotCounter': count,'defected_Y_N':defected_Y_N,'crack':cra, 'cavity':cav,
                                'dross':dro,'fin':fi,'shift':shift,'line':'Hydro 2 Line 1','section':'casting',
                                'weight':25,'supervisor':'Manoj Jain','operatorId':1 ,'resolved_Y_N':'N',
                                'uuid':uuid_val,'defectedType':'NAN','emptyTray': empty_tray_status,'operatorName':'Operator A','boundingBox':bbox}])
            #Push data into DB.
            #print(df)
            df.to_sql("casting",engine,if_exists = "append",index = False)
            print(df)
            algo8_python_logger.info({"message": "Casting Data Push Successfully INTO DB"})
            algo8_python_logger.info({"message": df})
            
#             algo8_python_logger.info({"time taken to get one complete inference": time.time()-time_infer})
        except Exception as e:
            algo8_python_logger.info({"message": e})
            
            
    return 'cav'


@app.route('/stacking_upload', methods=["POST"])
def predict_stack_upload():
    global batch,legged_ingot_count
    time_infer = time.time()
    if request.method =="POST":
        r=request
        count= r.json['generic_count']
        ingot_counter= r.json['ingot_counter']
        batch=r.json['batch']
        img= r.json['image']
        timestamp=r.json['timestamp']
        img_name=r.json['img_name']
        jpg_original=base64.b64decode(img)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
        print(img.shape)
        algo8_python_logger.info({"message": "Stacking Frames from folder Received"})
        algo8_python_logger.info({"message": "stacking frames process into yolov5 model"})
        #Yolov5 stacking model call
        contam, drip_mark, surface_rough,water_mark,hot_cold_shuts,brand_enboss,fi,uuid_val,now,bbox= stack_stacking_model(model2,img,count,img_name)
#         count+=1
        # Yolov5 legged ingots model call
        legged_ingot_status=stack_legged_ingots(img,legged_model)
        if legged_ingot_status:
            legged_ingot_count+=1
            if legged_ingot_count==1:
                batch+=1
            if legged_ingot_count==4:
                legged_ingot_count=0
        
        if contam+drip_mark+surface_rough+water_mark+hot_cold_shuts+brand_enboss+fi > 0:
            defected_Y_N = 'Y'
        else:
            defected_Y_N = 'N'  
        
        shift= check_shift()
#             algo8_python_logger.info({"message": "stacking frames process into legged_ingots model"})
        #Create a DataFrame to take all values and push in to DB.
        df = pd.DataFrame([{'timestamp':timestamp,'imageName':img_name,'leggedIngotStatus':legged_ingot_status,
                            'batch':batch,'ingotCounter':ingot_counter,'defected_Y_N': defected_Y_N,'contamination':contam,
                            'drippingMark':drip_mark, 'surfaceRoughness':surface_rough,
                            'waterMarking':water_mark,'hotAndColdShuts':hot_cold_shuts,
                            'brandEnbossing':brand_enboss,'fin':fi,'spuriousBatchStatus': 'NAN',
                            'shift':shift,'line':'Hydro 2 Line 2','section':'stacking','weight':25,'supervisor':'Manoj Jain',
                            'operatorName':'Operator A' ,'resolved_Y_N':'N','uuid':uuid_val,'imagePath':'NAN','defected':0,'operatorId':1,'boundingBox':bbox,'genericCounter':count}])
        #print(df)
        #Push data into DB.
        df.to_sql("stacking",engine,if_exists = "append",index = False)
        #print(df)
        algo8_python_logger.info({"message": "Stacking Data PUSH Successfully INTO DB"})
        # syncing the stacking data with casting data
        sync(df)
        algo8_python_logger.info({"message": "syncing mech"})
        
    return {'contam':contam,'drip_mark':drip_mark,'surface_rough':surface_rough,'water_mark':water_mark,'hot_cold_shuts':hot_cold_shuts,'brand_enboss':brand_enboss,'fi':fi}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask api exposing yolov5 model")
    parser.add_argument("--port", default=7000, type=int, help="port number")
    args = parser.parse_args()

      # force_reload = recache latest code
    app.run(host="0.0.0.0", port=args.port,debug=True)  # debug=True causes Restarting with stat
   