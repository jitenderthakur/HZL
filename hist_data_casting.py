import glob
import os.path
from datetime import datetime

import glob
import os.path
from datetime import datetime

def get_data(path):
	genericCounter=0

	file_type = '*.jpg'
	files = glob.glob(path + file_type)
	if files is not None:
		max_file = max(files, key=os.path.getctime)
		a = max_file.split('\\')
		s = a[6].split('_')
		s1 = s[7].split('.')
		genericCounter = int(s1[0])
	return  genericCounter

# path = 'C:\\Users\\cspsaa\\Documents\\hzl_pipeline\\casting_img\\*'
# file_type = '*.jpg'
# files = glob.glob(path + file_type)
# #if files is not None:
# max_file = max(files, key=os.path.getctime)

# a = max_file.split('\\')
# s = a[6].split('_')
# s1 = s[7].split('.')
# genericCounter = s1[0]
