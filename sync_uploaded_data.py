from sqlalchemy import create_engine
import pandas as pd
import time
import logging as lg
from datetime import datetime

logger = lg.basicConfig(filename = "log_files/"+"sync_"+str(datetime.now().date())+".log", 
                        level = lg.INFO, 
                        format = '%(asctime)s %(message)s')
algo8_python_logger = lg.getLogger()

# connecting to DB
try:
    connect_query = "mysql+pymysql://"+'admin'+":"+'Dev123456'+"@"+'hzl.cgwyhisjxon9.ap-south-1.rds.amazonaws.com'+":"+"3306"+"/"+"hzl"
    engine = create_engine(connect_query)
    algo8_python_logger.info({"message": "connected to DB successfuly"})

except:
    algo8_python_logger.info({"message": "Failed to connect with DB"})
    
    
def sync_kpi_data():
	sync_data = pd.read_sql_query(
	    ''' select *
            
			from sync_kpi where date(timestamp)= date(CONVERT_TZ(NOW(),'+00:00','+05:30'))''', engine)

	df1 = pd.DataFrame(sync_data)
	return df1


def sync(dfn):
    merge_data_table=0
    df_sync=sync_kpi_data()
    
    # find elements in dfn that are not in df_sync
    dfn = dfn[~(dfn['imageName'].isin(df_sync['imageName']))].reset_index(drop=True)

    d_stack=dfn[['imageName','batch','genericCounter', 'contamination','drippingMark','surfaceRoughness','waterMarking','hotAndColdShuts','brandEnbossing','fin']]

    cam2_count=d_stack['genericCounter'].values[0]-42
#         print(cam2_count)
    #fetching data from casting where ingot_counter==cam2_count
    casting_data = pd.read_sql_query('''select imageName,crack,cavity,dross,fin,timestamp,ingotCounter from casting where ingotCounter = %(n)s AND date(timestamp)= date(CONVERT_TZ(NOW(),'+00:00','+05:30'));''',engine,params={'n':cam2_count})
    df = pd.DataFrame(casting_data, columns=['imageName','crack','cavity','dross','fin','timestamp','ingotCounter'])
    df.rename(columns={'imageName': 'cast_imageName'}, inplace=True)
    df.rename(columns={'fin': 'fin_cast'}, inplace=True)
    df.rename(columns={'ingotCounter': 'cast_count'}, inplace=True)
    #print('casting_df ',df)
    if not df.empty:
        merge_data_table = pd.concat([d_stack.reset_index(drop=True),df.reset_index(drop=True)], axis=1,join='outer')
        algo8_python_logger.info({"message": "merge table  created sucessfully"})
        merge_data_table.to_sql("sync_kpi",engine,if_exists = "append",index = False)
    return merge_data_table
