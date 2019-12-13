#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

#from Python_mariadb_helper import MariadbHelper
import sqlite3

def getSqliteData(sqlite_file):
	conn = sqlite3.connect(sqlite_file)
	cur = conn.cursor()
	print("Opened WeChat database successfully")
	
	res = cur.execute("select * from ChatData")
	data = cur.fetchall()	
#	print(cur.fetchall())
#	msg_text = []
#	for row in cur:
#		msg_text.append(row[4])
#		print(row[4]) 
	
	cur.close()
	conn.close()
#	return msg_text
	return data

def countWordFrequency(data):
	import jieba
	from collections import Counter

	msg_text = []
	for row in data:
		msg_text.append(row[4])
#		print(row[4])
	
	c = Counter(msg_text).most_common(20)
	print("******* 词频Top20: *******")
	print("*** 已过滤部分图片消息 ***")
	for item in c:
		if len(item[0])>10:
			continue
		print(item[0], item[1])

	print("**************************")

def countDatetime(data):
	import time

	msg_datetime = []
	for row in data:
		msg_datetime.append(row[3])
#		print(row[3])
	# 格式化成2016-03-20 11:45:39形式
#	print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg_datetime[0])))

	msg_datetime.sort()
	for item in msg_datetime:
#		print(item)	
		pass


# 2012-08-16 01:28:33
def calTime(date1,date2):
	import time
	import datetime
	date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
#	date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
	date2=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
	date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
	date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
	print("Test ---> ", date2-date1)
	return date2-date1

#print cal_difftime('7时10分52秒', '10时20分50秒')
def cal_difftime_hour(time1, time2):
    # 字符串转换成日期格式数组
    time1array = time.strptime(time1, '%H时%M分%S秒')
    time2array = time.strptime(time2, '%H时%M分%S秒')
    # 因为默认年份为1900，转换时间戳的时候会出现报错
    # OverflowError: mktime argument out of range
    # timearray属于元组，不能修改其值
    # 所以我对其年份进行了修改
    time1array = (2018, 1, 1, time1array[3], time1array[4], time1array[5], 1, 1, 0)
    time2array = (2018, 1, 1, time2array[3], time2array[4], time2array[5], 1, 1, 0)
    # 日期格式数组转换成时间戳
    time1stamp = int(time.mktime(time1array))
    time2stamp = int(time.mktime(time2array))
    # 计算时间戳时间差
    timestamp = time2stamp - time1stamp
    m, s = divmod(timestamp, 60)
    h, m = divmod(m, 60)
    difftime = "%02d时%02d分%02d秒" % (h, m, s)
    return difftime

if __name__ == "__main__":
	file = "/Users/gdlocal1/Desktop/Cyril/Coding/Python/WeChat/data.sqlite"
	print("Hello lulu")
	
	love_time=calTime("2018-02-14 12:00:00","2019-01-31 12:00:00")
	print(love_time)
	print("From 18-02-14 12:00, we have met again in %s until now. 🎉🎉" %love_time)
	data=getSqliteData(file)
	countWordFrequency(data)
	countDatetime(data)


