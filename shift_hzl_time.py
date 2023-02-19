from datetime import datetime

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