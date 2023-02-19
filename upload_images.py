import json
import re
import glob
import time
import os
import base64
import json
import cv2
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
import requests
import numpy as np
import cv2
from datetime import datetime
# numbers = re.compile(r'(\d+)')


# def numericalSort(value):
#     parts = numbers.split(value)
#     parts[1::2] = map(int, parts[1::2])
#     return parts

#     for infile in sorted(glob.glob('*.txt'), key=numericalSort):
#         print("Current File Being Processed is: " + infile)
        
def remove_img(path, img_name):
    # this fxn will remove the images from the folder   
    # check if file exists or not
    if os.path.exists(path + '/' + img_name) is True:
        os.remove(path + '/' + img_name)
        return True
    
def casting_img_detail(name_cast):
    name_cast=name_cast.split('_')
    now = str(datetime.now().year)
    name_cast[1]=now
    date=" ".join(str(x) for x in name_cast[1:4]).replace(' ','-')
    time= " ".join(str(x) for x in name_cast[4:7]).replace(' ',':')
    timestamp=date+' '+time
    count=int(name_cast[7].split('.')[0])
    return timestamp,count

def stacking_img_detail(name):
    name=name.split('_')
    now = str(datetime.now().year)
    name[1]=now
    date=" ".join(str(x) for x in name[1:4]).replace(' ','-')
    time= " ".join(str(x) for x in name[4:7]).replace(' ',':')
    timestamp=date+' '+time
    generic_count= int(name[7:8][0])
    batch=int(name[8:9][0])
    ingot_count=int(name[9].split('.')[0])
    return timestamp,generic_count,batch,ingot_count

def upload_cast_img(files_path,url,headers):
    # this fxn will upload the images from folder to the SAP
   
    """file_path: path where all the images are stored
    url: url of api
    headers = {'content-type' : image/jpeg}
    """
    
    files = os.listdir(files_path)
#     files=sorted(files,key=numericalSort)
    
    # All the images will be appended in CV_img variable
    cv_img = []
    image_names=[]
    for path in files:

        if (str(path).endswith('png')) or (str(path).endswith('jpg')):
            path = files_path+'/'+path
            
            #storing image names
            image_names.append(path.split('/')[-1])
            #storing img in cv_img
            n= cv2.imread(path)
            cv_img.append(n)

    
    for i in range(len(cv_img)):
        jpg_img = cv2.imencode('.jpg', cv_img[i])[1]
        #converting img to b64 format
        b64_string = base64.b64encode(jpg_img).decode('utf-8')
        
        #feteching data from image name
        timestamp,count=casting_img_detail(image_names[i])
        img_name=image_names[i]
        print('---------------------uploading image ---------------------------------------')
        
        try:
#             data={'count':count,'image':img_encoded}
#             print(data)
            response = requests.request('POST',url,data=json.dumps({'timestamp':str(timestamp),
                                                                    'generic_count':str(count),
                                                                    'img_name':str(img_name),
                                                                    'image':b64_string}),headers=headers)
            print(response)
            
            #if frame is not saved 
            if response.status_code == 200:
                print('y')
                #delete the image from folder after uploading it 
                remove_img(files_path,files[i])
        except requests.HTTPError as exception:
            print(exception)
            continue
        
def upload_stack_img(files_path,url,headers):
    # this fxn will upload the images from folder to the SAP
   
    """file_path: path where all the images are stored
    url: url of api
    headers = {'content-type' : image/jpeg}
    """
    
    files = os.listdir(files_path)
#     files=sorted(files,key=numericalSort)
    
    # All the images will be appended in CV_img variable
    cv_img = []
    image_names=[]
    for path in files:

        if (str(path).endswith('png')) or (str(path).endswith('jpg')):
            path = files_path+'/'+path
            #storing image names
            image_names.append(path.split('/')[-1])
            
            n= cv2.imread(path)
            cv_img.append(n)
    
    for i in range(len(cv_img)):
        jpg_img = cv2.imencode('.jpg', cv_img[i])[1]
        #converting img to b64 format
        b64_string = base64.b64encode(jpg_img).decode('utf-8')
        
        #fetching details from image name
        timestamp,generic_count,batch,ingot_counter=stacking_img_detail(image_names[i])
        print(image_names[i])
        img_name=image_names[i]
        print('t:',timestamp,'g: ',generic_count,'b: ',batch,'in: ',ingot_counter)

        print('---------------------uploading image ---------------------------------------')
        
        try:
#             data={'count':count,'image':img_encoded}
#             print(data)
            response = requests.request('POST',url,data=json.dumps({'timestamp':str(timestamp),
                                                                    'ingot_counter':str(ingot_counter),
                                                                    'generic_count':str(generic_count),
                                                                    'batch':batch,
                                                                    'img_name':img_name,
                                                                    'image':b64_string}),headers=headers)
            print(response)
            
            #if frame is not saved 
            if response.status_code == 200:
                
                print('y')
                #delete the image from folder after uploading it 
                remove_img(files_path,files[i])
        except requests.HTTPError as exception:
            print(exception)
            continue

#every after 15mins all the frames that are stored in folder will be uploaded on SAP
content_type = 'application/json'
headers = {'Content-Type' : content_type}


addr = 'http://13.126.123.224:7000'
cast_test_url = addr + '/casting_upload'

cast_files_path='C:/Users/cspsaa/Documents/hzl_pipeline/failed_cast_img/'

stack_test_url = addr + '/stacking_upload'

stack_files_path='C:/Users/cspsaa/Documents/hzl_pipeline/failed_stack_img/'

#start the timer
start= time.perf_counter()
while True:
    if (time.perf_counter() -start)>9:
        print('uploading')
        #upload all the images from the folder 
        upload_cast_img(cast_files_path,cast_test_url,headers)
        print('upload_stack')
        upload_stack_img(stack_files_path,stack_test_url,headers)

        #start the timmer again
        start= time.perf_counter() 