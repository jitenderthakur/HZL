import glob
import os.path
from datetime import datetime

def get_data(path):
	genericCounter=0
	batch = 0
	legged_ingot_count = 0
	ingot_count = 1

	file_type = '*.jpg'
	files = glob.glob(path + file_type)
	if files is not None:
		max_file = max(files, key=os.path.getctime)

		a = max_file.split('\\')
		s = a[6].split('_')
		genericCounter = int(s[7])
		batch = int(s[8])
		s1 = s[9].split('.')
		ingot_count = int(s1[0])
	return genericCounter , batch , legged_ingot_count , ingot_count