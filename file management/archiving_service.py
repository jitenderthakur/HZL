import os
import time
from datetime import datetime

def delete_files(dir_path,limit_days):
    """this fxn will delete the files which are created at limit_days(eg:limit_days=1)
    dir_path: path of the dirctory where all the files are stored
    limit_days: days in int  """
    
    treshold = time.time() - limit_days*86400
    #name of the files will be stored in files valriable
    files=[]
    try:
        entries = os.listdir(dir_path)
        for dir in entries:
            creation_time = os.stat(os.path.join(dir_path,dir)).st_ctime
            if creation_time < treshold:
                print(f"{dir} is created on {time.ctime(creation_time)} and will be deleted")
                files.append(dir)
    except:
        print('no file')
    
    ## If file exists, delete it ##
    for i in range(len(files)):
        if os.path.isfile(dir_path+files[i]):
            os.remove(dir_path+files[i])
            print('delete')
#             algo8_python_logger.info({"message": "selected files removed"})
            
        else:    ## Show an error ##
            print("Error: %s file not found" % files)
            
first_event = True
limit_days=5
prev_day = 0
current_day = datetime.now().day
path= '/home/ubuntu/HZL/hzl_pipeline/defected_images/'
while True:
    try:
        if first_event == True:
            print("First event identified!")
            prev_day = current_day
            first_event = False
        current_day = datetime.now().day

        if current_day != prev_day:
            print('deleting files')
            delete_files(path,limit_days)
            prev_day = current_day

        time.sleep(3600)
    except Exception as e:
        print(e)
