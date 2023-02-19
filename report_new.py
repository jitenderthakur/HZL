
import pandas as pd
import fpdf
import schedule
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sqlalchemy import create_engine
from datetime import date
from datetime import datetime
from datetime import timedelta
import time
import logging as lg
from sent_report import sendReport

#logging
logger = lg.basicConfig(filename = "log_files/"+"report_creation"+str(datetime.now().date())+".log", 
                        level = lg.INFO, 
                        format = '%(asctime)s %(message)s')
algo8_python_logger = lg.getLogger()

# connect to database
connect_query = "mysql+pymysql://"+'admin'+":"+'Dev123456' + \
	"@"+'hzl.cgwyhisjxon9.ap-south-1.rds.amazonaws.com'+":"+"3306"+"/"+"hzl"
engine = create_engine(connect_query)


first_event = True
prev_hour = 0
current_hour = datetime.now().hour
prev_day = 0
current_day = datetime.now().day
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
algo8_python_logger.info({"time":dt_string})

def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else: #Over midnight
        return nowTime >= startTime or nowTime <= endTime

def check_shift():
    start_a = '06:00AM'
    end_a = '02:00PM'
    
    start_b = '02:00PM'
    end_b = '10:00PM'
    
    timeNow = datetime.today().strftime("%I:%M %p").replace(" ", "")
    
    
    time_a_End = datetime.strptime(end_a, "%I:%M%p")
    time_a_Start = datetime.strptime(start_a, "%I:%M%p")
    
    time_b_End = datetime.strptime(end_b, "%I:%M%p")
    time_b_Start = datetime.strptime(start_b, "%I:%M%p")
    
    timeNow = datetime.strptime(timeNow, "%I:%M%p")
   
    if isNowInTimePeriod(time_a_Start, time_a_End, timeNow):
        return 'A'
    
    elif isNowInTimePeriod(time_b_Start, time_b_End, timeNow):
        return 'B'
    
    else :
        return 'C' 


def img_pdf(dfn):
	"""img_pdf fxn will created the
		image report of defected ingot"""

	# path where defected images are stored
	algo8_python_logger.info({"message": "img pdf one hours started running"})
	out1 = '/home/ubuntu/HZL/hzl_pipeline/defected_images/'

	wid = 210
	he = 297

	# initalizing fpdf
	pdf = fpdf.FPDF()

	print("Creating PDF")
	#
	for file in dfn['imageName'][(dfn['crack'] >= 1) | (dfn['cavity'] >= 1) | (dfn['fin'] >= 1) | (dfn['dross'] >= 1)]:
		# defected image name with path is stored in output variable
		# e.g: 'C:/Users/cspsaa/OneDrive - Algo8.ai/hzl_testing/images/img.jpg'
		output = out1+file

		# add blank page in pdf
		pdf.add_page()

		# set font type_size
		pdf.set_font('Arial', 'B', 12)

		# timestamp of defected image
		curr_time = dfn['timestamp'][dfn['imageName'] == file].values[0]

		# defect count for the above image
		cavity = dfn['cavity'][dfn['imageName'] == file].values[0]

		crack = dfn['crack'][dfn['imageName'] == file].values[0]

		dross = dfn['dross'][dfn['imageName'] == file].values[0]

		fin = dfn['fin'][dfn['imageName'] == file].values[0]

		# adding ouptut in the pdf
		pdf.multi_cell(0, 5, 'TIME '+curr_time + '\n' + 'Cavity '+str(cavity) + '\n' +
					   'Crack '+str(crack) + '\n' + 'Dross '+str(dross) + '\n' + 'Fin '+str(fin))

		# apending the defected image
		try:
			pdf.image(output, 10, 40, wid/1.5,he/2.5)
		except:
			algo8_python_logger.info({"no image found": file})

	# final pdf path where pdf will be stored
	final_pdf_path = '/home/ubuntu/hzl_report/'

	# date time
	now = datetime.now()
	current_time = str(now.strftime("_%H"))
	curr_time = str(now.strftime("%H:%M:%S"))
	report_day = str(date.today())
	# saving pdf
	report_name='cast_'+report_day+current_time+".pdf"
	pdf.output(final_pdf_path+'cast_'+report_day+current_time+".pdf", "F")
	print('done_done')
	engine.execute('''insert into hzl.report (date, time, reportName, sent) values ('{}','{}','{}',0)'''.format(report_day,curr_time,report_name))
	algo8_python_logger.info({"message": "Insert Data into DataBase"})
	algo8_python_logger.info({"message": " Image PDF Sucessfully Created "})
    
def dataframe_to_pdf(df, path):
	"""this fxn will convert dataframe to pdf"""
	# https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib
	algo8_python_logger.info({"message": "Convert DataFrame to PDF"})
	
	fig, ax = plt.subplots(figsize=(12, 4))
	ax.axis('tight')
	ax.axis('off')
	the_table = ax.table(cellText=df.values,
						 colLabels=df.columns, loc='center')

	# https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
	today = str(date.today())
	now = datetime.now()
	curr_time = str(now.strftime("%H:%M:%S"))
	current_time = str(now.strftime("_%H"))
	pp = PdfPages(path+'cast_'+today+".pdf")
	engine.execute('''insert into hzl.report (date, time, reportName, sent) values ('{}','{}','{}',0)'''.format(today,curr_time,'cast_'+today+'.pdf'))
	print('data inserted')
	pp.savefig(fig, bbox_inches='tight')
	#sendReport("subject","HZL_PDF_REPORT_DAILY",pp,"shivam.kumar@algo8.ai","pramod.jangid@algo8.ai")
	pp.close()
    
def dataframe_to_pdf_shift(df, path,shift):
	"""this fxn will convert dataframe to pdf"""
	# https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib
	algo8_python_logger.info({"message": "Convert DataFrame to PDF"})
	
	fig, ax = plt.subplots(figsize=(12, 4))
	ax.axis('tight')
	ax.axis('off')
	the_table = ax.table(cellText=df.values,
						 colLabels=df.columns, loc='center')

	# https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
	today = str(date.today())
	now = datetime.now()
	curr_time = str(now.strftime("%H:%M:%S"))
	current_time = str(now.strftime("_%H"))
	report_name='cast_'+today+shift+'.pdf'
	pp = PdfPages(path+'cast_'+today+shift+".pdf")
	engine.execute('''insert into hzl.report (date, time, reportName, sent) values ('{}','{}','{}',0)'''.format(today,curr_time,report_name))  
    
	algo8_python_logger.info({"message": "Insert Data into DataBase"})
	pp.savefig(fig, bbox_inches='tight')
	#sendReport("subject","HZL_PDF_REPORT_SHIFT_WISE",pp,"shivam.kumar@algo8.ai","pramod.jangid@algo8.ai")
	pp.close()
    
#for stack
def stack_img_pdf(dfn):
	"""img_pdf fxn will created the
		image report of defected ingot"""

	# path where defected images are stored
# 	algo8_python_logger.info({"message": "img pdf one hours started running"})
	out1 = '/home/ubuntu/HZL/hzl_pipeline/defected_images/'

	wid = 210
	he = 297

	# initalizing fpdf
	pdf = fpdf.FPDF()

	print("Creating PDF")
	#
	for file in dfn['imageName'][dfn['defected_Y_N'] == 'Y' ]:
		# defected image name with path is stored in output variable
		# e.g: 'C:/Users/cspsaa/OneDrive - Algo8.ai/hzl_testing/images/img.jpg'
		output = out1+file

		# add blank page in pdf
		pdf.add_page()

		# set font type_size
		pdf.set_font('Arial', 'B', 12)

		# timestamp of defected image
		curr_time = dfn['timestamp'][dfn['imageName'] == file].values[0]

		# defect count for the above image
		contamination = dfn['contamination'][dfn['imageName'] == file].values[0]

		drippingMark= dfn['drippingMark'][dfn['imageName'] == file].values[0]

		surfaceRoughness= dfn['surfaceRoughness'][dfn['imageName'] == file].values[0]

		waterMarking= dfn['waterMarking'][dfn['imageName'] == file].values[0]
		hotAndColdShuts = dfn['hotAndColdShuts'][dfn['imageName'] == file].values[0]
		brandEnbossing = dfn['brandEnbossing'][dfn['imageName'] == file].values[0]
		fin = dfn['fin'][dfn['imageName'] == file].values[0]
        
		# adding ouptut in the pdf
		pdf.multi_cell(0, 5, 'TIME '+curr_time + '\n' + 'contamination '+str(contamination) + '\n' +
					   'drippingMark '+str(drippingMark) + '\n' + 'surfaceRoughness '+str(surfaceRoughness)
                       + '\n' + 'waterMarking '+str(waterMarking) + '\n' +
					   'hotAndColdShuts '+str(hotAndColdShuts) + '\n' +
					   'brandEnbossing '+str(brandEnbossing) + '\n' +
					   'fin '+str(fin))

		# apending the defected image
		try:
			pdf.image(output,10, 60, wid/1.5,he/2.5)
		except:
			algo8_python_logger.info({"no image found": file})

	# final pdf path where pdf will be stored
	final_pdf_path = '/home/ubuntu/hzl_report/'

	# date time
	now = datetime.now()
	current_time = str(now.strftime("_%H"))
	curr_time = str(now.strftime("%H:%M:%S"))
	report_day = str(date.today())
	# saving pdf
	report_name='stack_'+report_day+current_time+".pdf"
	pdf.output(final_pdf_path+'stack_'+report_day+current_time+".pdf", "F")
	print('done_done')
	engine.execute('''insert into hzl.report (date, time, reportName, sent) values ('{}','{}','{}',0)'''.format(report_day,curr_time,report_name))
	algo8_python_logger.info({"message": "Insert Data into DataBase"})
	algo8_python_logger.info({"message": " Stack Image PDF Sucessfully Created "})

def stack_dataframe_to_pdf(df, path):
	"""this fxn will convert dataframe to pdf"""
	# https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib
	algo8_python_logger.info({"message": "Convert stack DataFrame to PDF"})
	
	fig, ax = plt.subplots(figsize=(12, 4))
	ax.axis('tight')
	ax.axis('off')
	the_table = ax.table(cellText=df.values,
						 colLabels=df.columns, loc='center')

	# https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
	today = str(date.today())
	now = datetime.now()
	curr_time = str(now.strftime("%H:%M:%S"))
	current_time = str(now.strftime("_%H"))
	report_name='stack_'+today+'.pdf'    
	pp = PdfPages(path+'stack_'+today+".pdf")
	engine.execute('''insert into hzl.report (date, time, reportName, sent) values ('{}','{}','{}',0)'''.format(today,curr_time,report_name))
	print('data inserted')
	pp.savefig(fig, bbox_inches='tight')
	#sendReport("subject","HZL_PDF_REPORT_DAILY",pp,"shivam.kumar@algo8.ai","pramod.jangid@algo8.ai")
	pp.close()

def stack_dataframe_to_pdf_shift(df, path,shift):
	"""this fxn will convert dataframe to pdf"""
	# https://stackoverflow.com/questions/32137396/how-do-i-plot-only-a-table-in-matplotlib
	algo8_python_logger.info({"message": "Convert stack DataFrame to PDF"})
	
	fig, ax = plt.subplots(figsize=(12, 4))
	ax.axis('tight')
	ax.axis('off')
	the_table = ax.table(cellText=df.values,
						 colLabels=df.columns, loc='center')

	# https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
	today = str(date.today())
	now = datetime.now()
	curr_time = str(now.strftime("%H:%M:%S"))
	current_time = str(now.strftime("_%H"))
	report_name='stack_'+today+shift+'.pdf'
	pp = PdfPages(path+'stack_'+today+shift+".pdf")
	engine.execute('''insert into hzl.report (date, time, reportName, sent) values ('{}','{}','{}',0)'''.format(today,curr_time,report_name))  
    
	algo8_python_logger.info({"message": "Insert Data into DataBase"})
	pp.savefig(fig, bbox_inches='tight')
	#sendReport("subject","HZL_PDF_REPORT_SHIFT_WISE",pp,"shivam.kumar@algo8.ai","pramod.jangid@algo8.ai")
	pp.close()

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def stack_one_hr_pdf():
	"""this fxn will create pdf report of images
	with hourly time period"""
	# fetching previous 1hr data
	algo8_python_logger.info({"message": 'Fetch one hour data from DataBase'})
	data = pd.read_sql_query(''' select timestamp,imageName,contamination,drippingMark,surfaceRoughness,waterMarking,
    hotAndColdShuts,brandEnbossing,fin,defected_Y_N 
		from stacking where timestamp >= date_sub(CONVERT_TZ(NOW(),'+00:00','+05:30'), interval 1 hour);''', engine)

	# creating df of the above output
	df = pd.DataFrame(data)
	print("DataFrame Fetched with shape: ", df.shape)
	# convert df  to pdf
	if not df.empty:
		stack_img_pdf(df)
        
def stack_one_day_pdf():
	"""this fxn will create table pdf report
	with hourly time period of whole dayy"""
	
	#fetching previous 1day data
	algo8_python_logger.info({"message": "stack One day Data  Fetch from DataBase"})

	data= pd.read_sql_query('''select timestamp,contamination,drippingMark,surfaceRoughness,waterMarking,
    hotAndColdShuts,brandEnbossing,fin,defected_Y_N
		from stacking where timestamp >= date_sub(CONVERT_TZ(NOW(),'+00:00','+05:30'),INTERVAL 1 DAY);''',engine)
	# creating df of the above output
	df=pd.DataFrame(data)

	if not df.empty:
		#convert it to datetime
		df['timestamp']= pd.to_datetime(df['timestamp'])

		# add total defected column
		df['total_defected_ingots']=df[['defected_Y_N']].apply(lambda x: 0 if  x[0]=='N'  else 1,axis=1)
		
		#add column total ingot
		df['total_ingots']=1
		# resampling df
		df= df.set_index('timestamp').resample('60min').sum()
		
		#converting inddex to column
		df=df.reset_index().rename({'index':'index1'},axis='columns')
		#convert df to pdf
		# final pdf path where pdf will be stored
		final_pdf_path = '/home/ubuntu/hzl_report/'
		stack_dataframe_to_pdf(df,final_pdf_path)
		algo8_python_logger.info({"message": "Sucessfully Saved stack one day pdf "})

def stack_shift_pdf(prev_shift):
	"""this fxn will create table pdf report
	with hourly time period of whole dayy"""
	
	#fetching previous 1day data
	algo8_python_logger.info({"message": "8 hour Data Fetch from stack table"})

	data= pd.read_sql_query('''select timestamp,contamination,drippingMark,surfaceRoughness,waterMarking,
    hotAndColdShuts,brandEnbossing,fin,defected_Y_N,shift
		from stacking where timestamp >= DATE_SUB(NOW(),INTERVAL 8 HOUR);''',engine)
	# creating df of the above output
	df=pd.DataFrame(data)
	
	
	df=df[df['shift']==prev_shift]
	
	if not df.empty:
		#convert it to datetime
		df['timestamp']= pd.to_datetime(df['timestamp'])

		# add total defected column
		df['total_defected_ingots']=df[['defected_Y_N']].apply(lambda x: 0 if  x[0]=='N'  else 1,axis=1)
		
		#add column total ingot
		df['total_ingots']=1
		# resampling df
		df= df.set_index('timestamp').resample('60min').sum()
		
		#converting inddex to column
		df=df.reset_index().rename({'index':'index1'},axis='columns')
		
		#convert df to pdf
		# final pdf path where pdf will be stored
		final_pdf_path = '/home/ubuntu/hzl_report/'
		stack_dataframe_to_pdf_shift(df,final_pdf_path,prev_shift)
		algo8_python_logger.info({"message": "Sucessfully Saved stack shift_wize pdf "})

# logic for running one_hr_pdf() after every hour

# ////////////////////////////////////////////////////////////////////////////////////////////////

def one_hr_pdf():
	"""this fxn will create pdf report of images
	with hourly time period"""
	# fetching previous 1hr data
	algo8_python_logger.info({"message": 'Fetch one hour data from DataBase'})
	data = pd.read_sql_query(''' SELECT timestamp,imagePath,imageName,ingotCounter,crack,cavity,dross,fin 
		from casting where timestamp >= date_sub(CONVERT_TZ(NOW(),'+00:00','+05:30'), interval 1 hour);''', engine)

	# creating df of the above output
	df = pd.DataFrame(data, columns=['timestamp', 'imagePath', 'imageName', 'ingotCounter', 'crack', 'cavity', 'dross', 'fin'])
	print("DataFrame Fetched with shape: ", df.shape)
	# convert df  to pdf
	if not df.empty:
		img_pdf(df)
		# logger.info({"message:":'image pdf created',"time:":t})
		algo8_python_logger.info({"message": "Sucessfully Convrted DataFrame to PDF"})

def one_day_pdf():
	"""this fxn will create table pdf report
	with hourly time period of whole dayy"""
	
	#fetching previous 1day data
	algo8_python_logger.info({"message": "One day Data Fetch from DataBase"})

	data= pd.read_sql_query('''select timestamp,imagePath,imageName,crack,cavity,dross,fin
		from casting where timestamp >= date_sub(CONVERT_TZ(NOW(),'+00:00','+05:30'),INTERVAL 1 DAY);''',engine)
	# creating df of the above output
	df=pd.DataFrame(data,columns=['timestamp','imagePath','imageName','crack','cavity','dross','fin'])

	if not df.empty:
		#convert it to datetime
		df['timestamp']= pd.to_datetime(df['timestamp'])

		# add total defected column
		df['total_defected_ingots']=df[['crack','cavity','dross','fin']].apply(lambda x: 0 if  x[0]==0 | x[1]==0 | x[2]==0 | x[3]==0 else 1,axis=1)
		
		#add column total ingot
		df['total_ingots']=1
		# resampling df
		df= df.set_index('timestamp').resample('60min').sum()
		
		#converting inddex to column
		df=df.reset_index().rename({'index':'index1'},axis='columns')
		#convert df to pdf
		# final pdf path where pdf will be stored
		final_pdf_path = '/home/ubuntu/hzl_report/'
		dataframe_to_pdf(df,final_pdf_path)	
		algo8_python_logger.info({"message": "Sucessfully Saved one day pdf "})

def shift_pdf(prev_shift):
	"""this fxn will create table pdf report
	with hourly time period of whole dayy"""
	
	#fetching previous 1day data
	algo8_python_logger.info({"message": "8 hour Data Fetch from DataBase"})

	data= pd.read_sql_query('''select timestamp,imagePath,imageName,crack,cavity,dross,fin,shift
		from casting where timestamp >= DATE_SUB(NOW(),INTERVAL 8 HOUR);''',engine)
	# creating df of the above output
	df=pd.DataFrame(data,columns=['timestamp','imagePath','imageName','crack','cavity','dross','fin','shift'])
	
	
	df=df[df['shift']==prev_shift]
	
	if not df.empty:
		#convert it to datetime
		df['timestamp']= pd.to_datetime(df['timestamp'])

		# add total defected column
		df['total_defected_ingots']=df[['crack','cavity','dross','fin']].apply(lambda x: 0 if  x[0]==0 | x[1]==0 | x[2]==0 | x[3]==0 else 1,axis=1)
		
		#add column total ingot
		df['total_ingots']=1
		# resampling df
		df= df.set_index('timestamp').resample('60min').sum()
		
		#converting inddex to column
		df=df.reset_index().rename({'index':'index1'},axis='columns')
		
		#convert df to pdf
		# final pdf path where pdf will be stored
		final_pdf_path = '/home/ubuntu/hzl_report/'
		dataframe_to_pdf_shift(df,final_pdf_path,prev_shift)
		algo8_python_logger.info({"message": "Sucessfully Saved shift_wize pdf "})


prev_shift=''
curr_shift= check_shift()

while True:
    try:
        algo8_python_logger.info({"message": "code started"})
        if first_event == True:
            print("First event identified!")
            prev_hour = current_hour
            # prev_day = current_day
            prev_shift=curr_shift
            first_event = False
        print("Time: ",datetime.now())
        current_hour = datetime.now().hour
        # current_day = datetime.now().day
        curr_shift= check_shift()
        print("Previous and Current Values: ",prev_hour,current_hour)

        if current_hour != prev_hour:
            #cast one hour pdf
            algo8_python_logger.info({"message": "cast one hr pdf"})
            one_hr_pdf()
    
            #stack one hour pdf
            algo8_python_logger.info({"message": "stack one hr pdf"})
            stack_one_hr_pdf()
            
            prev_hour = current_hour

        if curr_shift!=prev_shift:
            print(prev_shift)
            # cast shift pdf
            algo8_python_logger.info({"message": "cast shift pdf"})
            shift_pdf(prev_shift)
            
            # stack shift pdf
            algo8_python_logger.info({"message": "stack shift pdf"})
            stack_shift_pdf(prev_shift)
            
            prev_shift=curr_shift
            print('shift')

        if current_hour==22:
            #cast one day pdf
            algo8_python_logger.info({"message": "cast one day pdf"})
            one_day_pdf()
            
            #stack one day pdf
            algo8_python_logger.info({"message": "stack one day pdf"})
            stack_one_day_pdf()
            
            print('day')
            time.sleep(3600)
        else:
            time.sleep(600)
    except Exception as e:
        algo8_python_logger.info({"error": e})
#sendReport("subject","HZL_PDF_REPORT","2022-04-04A.pdf","jitender.thakur@algo8.ai","shivam@algo8.ai")