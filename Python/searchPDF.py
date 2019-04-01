#!/usr/bin/python3
# -*- encoding:UTF-8 -*-

import os,re

parent_path = "./"

# file_dir 只能是目录路径，而不能包含文件名
def file_name(file_dir):   
    for root, dirs, files in os.walk(file_dir):  
   #     print(root) #当前目录路径  
   #     print(dirs) #当前路径下所有子目录  
        return files #当前路径下所有非目录子文件  


files =  file_name("./")


def get_YPD():
	for item in files:
    
	    y = None  	## time
	    prov = None	## province
	    d = None	## date

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
	        d = "None"
	    if y and prov and d:
	        print("%s\t%s\t%s" %(y,prov,d))
	#    print(d)

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
				print("file: %s -> %s " %(file,dt.group()))
				break	## 找到即退出
#	return txt

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
				print("file: %s -> %s " %(file,dt.group()))
				break	## 找到即退出
#	return txt

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
				#return dt.group()[1:-1]
				txt.append(dt.group()[1:-1])
	return txt

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

	ofiles = getOfiles()
	for item in ofiles:
#		getDateTime(item)
#		getVehicleType(item)

#		print("file: %s, peopleStatus: %s" %(item, getPeopleStatus(item)))
#		print("file: %s, Econmic loss: %s" %(item, getMoney(item)))
#		print("file: %s, Road Type: %s" %(item, getRoadType(item)))
#		print("file: %s, Road Surface: %s" %(item, getRoadSurface(item)))
		print("file: %s, Weather: %s" %(item, getWeather(item)))

		
