#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

from bs4 import BeautifulSoup
from crawler_agent import getEISPHTML

def parse_PunchTime_HTML():
	"""
	parse_PunchTime_HTML function 解析考勤HTML数据
	"""
	print("================ parse_PunchTime_HTML BEGIN ================")
	with open("/Users/gdlocal1/Desktop/Cyril/Coding/Python/Study/getPunchTime.html","r") as f:
		html_str=f.read()
	soup = BeautifulSoup(html_str,'html.parser')
	tab_data=soup.find_all('td')
	print("================ parse_PunchTime_HTML END ================")
	return getTableList(col=7, tab_data=tab_data)  #表单数据为7列
	

def getTableList(col,tab_data):
	"""getTableList function 将源数据转化为列表
	param 'col': table columns
	param 'tab_data': original data type<soup.find_all> 
	"""
	data_all=[]
	data_record=[]
	i=0
	for item in tab_data:
		if i<col:
			data_record.append(item.text)
			i+=1
		elif i==col:
			data_all.append(data_record)
			data_record=[]
			i=0
		else:
			pass
	del data_all[-1]
	return data_all

def calcuPunchTimeByDay(arrayList):
	'''calcuPunchTimeByDay function 计算每日加班时数
	
	'''
	print("================ calcuPunchTimeByDay BEGIN ================")
	ls=arrayList
	dic_punchdate=dict()
	list_punchtime=list()
	for i in range(len(ls)):
		if i>0:
			if ls[i][5]!=ls[i-1][5]:
				list_punchtime=list()
			list_punchtime.append(ls[i][6])
			dic_punchdate[ls[i][5]]=list_punchtime

#	print(dic_punchdate) # 此处已将刷卡时间转化成如下格式
			     # {'2018/11/01': ['07:51:09', '17:41:25', '19:31:43'], 
			     #	'2018/11/02': ['07:57:33', '18:40:52'], ...}
	print("刷卡日期 : 星期数 : 加班时数(H)")
	total=0 #总加班时数
	for key in dic_punchdate.keys():
		dic_punchdate[key].sort()
		week = calcuWeek(key) #计算星期几
		work_class=judgeClass(dic_punchdate[key][0]) #计算班别
		
		if work_class == 0: #白班
			timeinterval_hr=calcuTimeInterval('17:30:00',dic_punchdate[key][-1]) #这是白班加班的计算方法
			if week == 6 or week == 7:
				timeinterval_hr=calcuTimeInterval(dic_punchdate[key][0],dic_punchdate[key][-1])-1.5 #星期六 星期天 算上下班打卡时间
		elif work_class == 1: #中班
			timeinterval_hr=calcuTimeInterval('12:00:00',dic_punchdate[key][-1]) #这是中班加班的计算方法
			if week == 6 or week ==7:
				timeinterval_hr=calcuTimeInterval(dic_punchdate[key][0],dic_punchdate[key][-1])-0.5 #星期六 星期天 算上下班打卡时间
		elif work_class == 2: #晚班 
			timeinterval_hr=calcuTimeInterval('22:00:00',dic_punchdate[key][-1]) #这是晚班加班的计算方法
			if week == 6 or week ==7:
				timeinterval_hr=calcuTimeInterval(dic_punchdate[key][0],dic_punchdate[key][-1])-1 #星期六 星期天 算上下班打卡时间
		else: #打卡时间异常,不计加班时数
			timeinterval_hr=0
		
		timeinterval_hr=calcuTimeInterval_calibration(timeinterval_hr, work_class, week)

		total=total+timeinterval_hr
		print(key," : ", week, " : ", timeinterval_hr)
		
	print("加班时数(H) Total:",total)
	print("================ calcuPunchTimeByDay END ================")

def calcuTimeInterval_calibration(timeinterval, work_class, week):
	'''calcuTimeInterval_calibration 时间差值校准 根据下班打卡时间差及班别判断
	param ‘timeinterval’: %H 未校准过的时间
	param 'work_class': int 班别  白0/中1/晚2
	param 'week': int 星期数
	'''
	threshold=0.09 #设定时间阈值为0.09h, 即约为5分钟
	if work_class==0:
		point=0.5
	elif work_class==1 or work_class==2:
		point=1
	else: # 异常
		point=0
	
	if timeinterval >= 2-threshold and timeinterval < 4: # 不超过4H的打卡时间都算正常2h
		timeinterval=2
	elif timeinterval > 0 and timeinterval < 2:
#		timeinterval=float("%.2f" %timeinterval)
		tmp=timeinterval-int(timeinterval)
		if tmp > point - threshold:
			timeinterval=int(timeinterval) + point #提前5分钟打卡算一个小时 
		else:					#即使补偿5分钟也达不到0.5h或1.0h则只算.0h或.5h
			timeinterval=int(timeinterval) + point - 0.5
	elif timeinterval >= 4-threshold and timeinterval < 12 and (week == 6 or week ==7):
#		timeinterval=float("%.2f" %timeinterval)
		tmp=timeinterval-int(timeinterval)
		if tmp > point - threshold:
			timeinterval=int(timeinterval) + point #提前5分钟打卡算一个小时
		else:                                   #即使补偿5分钟也达不到0.5h或1.0h则只算.0h或.5h
			timeinterval=int(timeinterval) + point - 0.5
	else:   #其他情况算异常，不计当天加班时数
		timeinterval=0
	return timeinterval

def judgeClass(puncktime):
	'''judgeClass function 判断班别
	param 'puncktime': "%H:%M:%S" # 以上班打卡时间计，判断班别
	## 白班 0
	## 中班 1
	## 晚班 2
	'''	
	threshold=2	# 设定判断阈值为2个小时

	if calcuTimeInterval("08:00:00",puncktime) < 2 :
		#print("白班")
		return 0
	elif calcuTimeInterval("13:00:00",puncktime) < 2 :
		#print("中班")
		return 1
	elif calcuTimeInterval("20:00:00",puncktime) < 2 :
		#print("晚班")
		return 2
	else:
		#print("Unknow Work Class")
		return -1
		
def calcuWeek(date=""):
	'''calcuWeek function 计算星期几
	param 'date':default "" #默认为空，即计算今天星期几
	param 'date': '%Y/%M/%D' #给指定日期，计算当天星期几:
	'''
	import time
	import datetime
	if date:
		dsplit=date.split("/",2)
		anyday=datetime.date(int(dsplit[0]),int(dsplit[1]),int(dsplit[2])).strftime("%w")
		return int(anyday)
	else:
		today=int(time.strftime("%w"))
		return int(today)
		 
	
def calcuTimeInterval(startTime, endTime):
	'''calcuTimeInterval function 计算时间差
	param 'startTime': "%H:%M:%S"
	param 'endTime': "%H:%M:%S"
	return 'timeinterval': int , hour
	'''
	import datetime
	d1=datetime.datetime.strptime(str(startTime), "%H:%M:%S")	
	d2=datetime.datetime.strptime(str(endTime), "%H:%M:%S")
	
	timeinterval_hr=(d2-d1).seconds/3600
	if timeinterval_hr > 12:
		timeinterval_hr=(d1-d2).seconds/3600
#	print(timeinterval_hr)
	return timeinterval_hr
	

if __name__ == "__main__":
	pwd="\u0043\u0079\u0072\u0069\u006c\u0032\u0030\u0031\u0038\u0031\u0030"
	getEISPHTML('F1235027',"Cyril201811")

	ls=parse_PunchTime_HTML() 
	for item in ls:
		print(item)

	# 计算超时加班时数
	calcuPunchTimeByDay(ls)

