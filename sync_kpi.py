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

def batch_num():
	stacking_data = pd.read_sql_query(
	    ''' select 
            batch
			from stacking ORDER BY timestamp DESC LIMIT 1;''', engine)

	df1 = pd.DataFrame(stacking_data, columns=['batch'])
# 	print(df1.values)
	if not df1.empty:
	    return df1['batch'].values[0]
	else:
	    return 0
    
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
    for i in range(len(dfn)):
        d_stack=dfn[['imageName','batch','genericCounter', 'contamination','drippingMark','surfaceRoughness','waterMarking','hotAndColdShuts','brandEnbossing','fin']].iloc[i]
        d_stack=pd.DataFrame(d_stack)
        d_stack=d_stack.T
        #cam2_ingot_counter-42
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
            algo8_python_logger.info({"message": "merge table created sucessfully"})
            merge_data_table.to_sql("sync_kpi",engine,if_exists = "append",index = False)
    return merge_data_table

#start the timer
start= time.perf_counter()

while True:
    try:
        if time.perf_counter()-start>900:
            start= time.perf_counter()
            batch=batch_num()-5
            print(batch)
            if batch>=4:
                #fetching rows from prev 5 batch
                stacking_data = pd.read_sql_query(''' select * from stacking where batch > %(n)s AND date(timestamp)= date(CONVERT_TZ(NOW(),'+00:00','+05:30'));''',engine,params={'n':batch})
                algo8_python_logger.info({"message": "fetched previous 5 batch data from stacking"})
            #     print(stacking_data)
                df_stack = pd.DataFrame(stacking_data)

                for i in range(batch+1,batch+6):
                    if i<batch+5:
                        print('i: ',i)
                        #getting first row of 1st batch where legged_status==1
                        df2=df_stack[(df_stack['batch']==i) & (df_stack['leggedIngotStatus']==1)][0:1]
            #             print(df2)
                        algo8_python_logger.info({"message": "storing first row of 1st batch where legged_status==1 in df2"})

                        #getting first row of 2nd batch  where legged_status==1
                        df3=df_stack[(df_stack['batch']==i+1) & (df_stack['leggedIngotStatus']==1)][0:1]
                        algo8_python_logger.info({"message": "storing first row of 2nd batch where legged_status==1 in df3"})
            #             print(df3)
                    #     print(df2,df3)

                        #checking diff between genric_count from batch1 legged to batch2 
                        dif=df3['genericCounter'].values[0]-df2['genericCounter'].values[0]
                        change_count=40-dif
                        algo8_python_logger.info({"difference between ingot_counter in two batches": change_count})
                        print('chng_count',change_count)

                        #if dif >=1 then add the diff to the ingotCounter
                        if change_count>=1:
                            print('change')

                            #getting df from where we want to add the change_count
                            algo8_python_logger.info({"message": "getting df from where we want to add the change_count"})

                            dfn=df_stack[df_stack['genericCounter']>=df3['genericCounter'].values[0]]
                            dfn['genericCounter']=dfn['genericCounter']+change_count
                            algo8_python_logger.info({"message": "stacking ingot_counter updated"})


                    else:
                        print('-----------------------------------------')
                        #dropping rows from df_stack 
                        try:
                            b=dfn['batch'].values[0]
                            df_stack.drop(df_stack.loc[df_stack['batch']>=b].index,inplace=True)
                            algo8_python_logger.info({"message": 'drop rows from df_stack'})

                            #combining new df to df1
                            df_stack=pd.concat([df_stack,dfn])
                        except Exception as e:
                            algo8_python_logger.info({"error": e})

                        # delete the rows from db
                        try:
                            d = pd.read_sql_query(''' delete from stacking where batch > %(n)s AND date(timestamp)= date(CONVERT_TZ(NOW(),'+00:00','+05:30'));''',engine,params={'n':batch})
                            algo8_python_logger.info({"message": "deleted rows from stacking"})
                        except Exception as e:
                            algo8_python_logger.info({"error": e})


                        try:
                            #appending new df to db

                            df_stack.to_sql("stacking",engine,if_exists = "append",index = False)
                            algo8_python_logger.info({"message": "appended new df to db"})

                            #now sync casting and stacking
                            algo8_python_logger.info({"message": "calling sync fxn"})
                            sync(df_stack)

                        except Exception as e:
                            algo8_python_logger.info({"error": e})
                        break


            else:
                print('no 5 batch')
                algo8_python_logger.info({"message": "no 5 batches found"})
    except Exception as e:
        print("error",e)
        algo8_python_logger.info({"error": e})
        
