#!/usr/bin/python3
# -*- encoding:UTF-8 -*-

import os,re
import csv

parent_path = "./"

# file_dir 只能是目录路径，而不能包含文件名
def file_name(file_dir):   
    for root, dirs, files in os.walk(file_dir):  
   #     print(root) #当前目录路径  
   #     print(dirs) #当前路径下所有子目录  
        return files #当前路径下所有非目录子文件  


#files =  file_name("./")


## 勿用
def get_YPD():

	y = None  	## time
	prov = None	## province
	d = None	## date

	YPD=[]
	for item in files:
    
#		y = None  	## time
#		prov = None	## province
#		d = None	## date
#		yield [y,prov,d]

		print("item -> %s" %item)
		_y = re.match("[0-9]{4}",item)
		if _y:
			y = _y.group()

		regex_str = "[\u4E00-\u9FA5]+"
		_prov = re.search(regex_str,item)
		if _prov:
			prov = _prov.group()
    
		regex_str = "[\u4E00-\u9FA5]\d+.\d+"
		_d = re.search(regex_str,item)
		if _d:
			#print(prov.group())
			d = _d.group()[1:]
        
		if y == "2011" and prov == "新疆":
			d = None

		if y and prov and d:
			YPD.append([y,prov,d])
	return YPD




def getOfiles():
	"""
	# 获取当前目录下所有待扫描的txt文档
	"""
	files=file_name(parent_path)
	ofiles=[]

	for item in files:
		if item[-4:] == ".txt":
			ofiles.append(item)
	return ofiles


def getDateTime(file):
	pattern='[0-9]{4}[\u4E00-\u9FA5]\d+[\u4E00-\u9FA5]\d+[\u4E00-\u9FA5]\d+[\u4E00-\u9FA5]'
	txt = []
	with open(file) as f:
		for line in f:
			#print(line)
			dt = re.search(pattern, line)
			if dt:
				#print("file: %s -> %s " %(file,dt.group()))
				#break	## 找到即退出
				return dt.group()

def getVehicleType(file):
	"""
	# 获取车型
	"""
	pattern='[\u4E00-\u9FA5]型[\u4E00-\u9FA5]{1,6}车'
	txt = []
	with open(file) as f:
		for line in f:
			#print(line)
			dt = re.search(pattern, line)
			if dt:
				#print("file: %s -> %s " %(file,dt.group()))
				#break	## 找到即退出
				return dt.group()

def getPeopleStatus(file):
	"""
	# 获取人员伤亡情况
	"""	
	p_dead='\d+人死亡'
	p_injured='\d+人受伤'
	p_misssing='\d+人失踪'
	
	dead=None
	injured=None
	missing=None
	
	with open(file) as f:
		for line in f:
			#print(line)
			dt_dead = re.search(p_dead, line)
			if dt_dead and (not dead):
				dead=dt_dead.group()
			
			dt_injured = re.search(p_injured, line)
			if dt_injured and (not injured):
				injured=dt_injured.group()	
			
			dt_missing = re.search(p_misssing, line)
			if dt_missing and (not missing):
				missing=dt_missing.group()

			if dead and injured and missing:
				break	## 找到即退出
	return (dead, injured, missing)


def getMoney(file):
	pattern='直接经济损失(.*)元'
	txt = []
	with open(file) as f:
		for line in f:
			#print(line)
			dt = re.search(pattern, line)
			if dt:
				#print("file: %s -> %s " %(file,dt.group()))
				#break	## 找到即退出
				return dt.group()[6:]
	
def getRoadType(file):
	pattern='，[\u4E00-\u9FA5]{1,5}车道，'
	txt = []
	with open(file) as f:
		for line in f:
			#print(line)
			dt = re.search(pattern, line)
			if dt:
				#print("file: %s -> %s " %(file,dt.group()))
				#break	## 找到即退出
				return dt.group()[1:-1]

def getRoadSurface(file):
	pattern='，[\u4E00-\u9FA5]{1,5}路面，'
	txt = []
	with open(file) as f:
		for line in f:
			#print(line)
			dt = re.search(pattern, line)
			if dt:
				#print("file: %s -> %s " %(file,dt.group()))
				#break	## 找到即退出
				return dt.group()[1:-1]
				#txt.append(dt.group()[1:-1])
#	return txt[0]

def getWeather(file):
	pattern='为[\u4E00-\u9FA5]+天气'
	txt = []
	with open(file) as f:
		for line in f:
			#print(line)
			dt = re.search(pattern, line)
			if dt:
				#print("file: %s -> %s " %(file,dt.group()))
				#break	## 找到即退出
				return dt.group()[1:-2]
	
if __name__ == "__main__":

	y = None  	## time
	prov = None	## province
	d = None	## date

	ofiles = getOfiles()

	out = open('info.csv','a', newline='')
	csv_write = csv.writer(out,dialect='excel')
	

	print("=====================================================================================================================")
	print("省份	年份	事故发生时间	涉及车辆	死亡人数	受伤人数	直接经济损失	车道	路面	天气")

	for item in ofiles:
   
		YPD=[]
#		y = None  	## time
#		prov = None	## province
#		d = None	## date
#		yield [y,prov,d]

		_y = re.match("[0-9]{4}",item)
		if _y:
			y = _y.group()

		regex_str = "[\u4E00-\u9FA5]+"
		_prov = re.search(regex_str,item)
		if _prov:
			prov = _prov.group()
    
		regex_str = "[\u4E00-\u9FA5]\d+.\d+"
		_d = re.search(regex_str,item)
		if _d:
			#print(prov.group())
			d = _d.group()[1:]
        
		if y == "2011" and prov == "新疆":
			d = None

		if y and prov and d:
			YPD=[y,prov,d]
		else:
			continue


#		getDateTime(item)
#		getVehicleType(item)

#		print("file: %s, peopleStatus: %s" %(item, getPeopleStatus(item)))
#		print("file: %s, Econmic loss: %s" %(item, getMoney(item)))
#		print("file: %s, Road Type: %s" %(item, getRoadType(item)))
#		print("file: %s, Road Surface: %s" %(item, getRoadSurface(item)))
#		print("file: %s, Weather: %s" %(item, getWeather(item)))

		DIM=getPeopleStatus(item) #Dead, Injured, Missing
		if not DIM:
			DIM=[None,None,None]
		
		if  getDateTime(item):
			YPD[2] = getDateTime(item)	

		print("%s	%s	%s		%s	%s	%s	%s		%s	%s	%s" %(YPD[1],YPD[0],YPD[2],getVehicleType(item),DIM[0],DIM[1],getMoney(item),getRoadType(item),getRoadSurface(item),getWeather(item)))	

		info_row=[YPD[1],YPD[0],YPD[2],getVehicleType(item),DIM[0],DIM[1],getMoney(item),getRoadType(item),getRoadSurface(item),getWeather(item)]	
		csv_write.writerow(info_row)
		
		

	print("=====================================================================================================================")

