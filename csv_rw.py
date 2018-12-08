# -*- coding:UTF-8 -*-
# --csv 文件读写操作2 --
# Create on 18/12/05 by Cyril

import csv
import os, sys

def print2DList(_2DList):
	if _2DList:
		try:
			for line in _2DList:
				print(line)
		except Exception as e:
			print("print2DList -> Error _2DList data type.")
			print(e)
		finally:
			print("print2DList -> Finish.")

# 读取csv文件 (obj.dict)
def readCSVFile(filePath):
	if(os.path.exists(filePath)):
		mdata=[]
		with open(filePath, 'r') as f:
			lines = csv.reader(f)	
			for line in lines:
				mdata.append(line)
	else:
		print('readCSVFile -> no file:', filePath)
	print2DList(mdata)
	print ("readCSVFile -> Reading successful.")
	return mdata

# 写入csv文件（obj.dict）
def writeCSVFile(filePath, _2DList):
	if(os.path.exists(filePath)):
#		csvfile = open(filePath, 'a', newline='') # newline='' 为python3
		csvfile = open(filePath, 'a')
		writer_ = csv.writer(csvfile, dialect='excel')
		if isinstance(_2DList, (list)):
			try:
				for line in _2DList:
					writer_.writerow(line)
				print ("writeCSVFile -> Writing successful.")
			except Exception as e:
				print ("writeCSVFile -> Error data type")
				print("TEST -> ",e)
		else:
			print ("writeCSVFile -> Error data type")
		pass
	else:
		dirname, filename = os.path.split(os.path.abspath(filePath))
		if(os.access(dirname, os.W_OK)):  #检查路径是否可写，即是否可创建文件
			cmd = 'cd '+ dirname + ' ; touch ' + filename + ' ;'
			os.system(cmd)
			writeCSVFile(filePath, _2DList)
			return True
		else:
			print("writeCSVFile -> Current path no access to create files.")
			return False

if "__main__" == __name__:
	dirname, filename = os.path.split(os.path.abspath(sys.argv[0])) 
	filePath = dirname+"/csvData.csv"
	print("filePath : ", filePath)

	data=[]
	data.append(['1', 'a', '123'])
	data.append(['2', 'b', '223'])
	data.append(['3', 'c', '133'])
	data.append(['4', 'd', '321'])
	data.append(['5', 'e', '333'])
	writeCSVFile(filePath, _2DList=data)
	readCSVFile(filePath)

