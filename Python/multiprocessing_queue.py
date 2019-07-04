#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
from multiprocessing import Process, Pipe
import time
import os

"""
多进程间通信
"""


class ClockProcess(Process):

    def __init__(self,value):
        self.value = value
        super(ClockProcess,self).__init__()

    def run(self):
        for i in range(5):
            print("现在的时间是",time.ctime())
            time.sleep(self.value)

def ClockProcessTest():
	# 创建自定义进的类的对象
	p =ClockProcess(2)

	# 自动调用run
	p.start()
	p.join()

import pickle, gzip
def save(filename, *objects):
	#with open(filename, "wb", encoding="utf-8") as f:
	fil = None
	try:
		fil = gzip.open(filename,'wb')
		for obj in objects:
			pickle.dump(obj,fil)
	except Exception as e:
		print (e)
	finally:
		if fil:
			fil.close()

def load(filename):
	fil = None
	try:
		fil = gzip.open(filename, 'rb')
		return pickle.load(fil)
#		while True:
#			try:
#				data = pickle.load(fil)
#				yield data
#				return data
#			except EOFError:break
	except Exception as e:
		#print(e)
		return None
	finally:
		if fil:
			fil.close()

filename = "/tmp/test_msg.txt"

#多进程消息队列传递数据
from multiprocessing import Queue,Process
from time import sleep
import multiprocessing

# 创建队列，可以放3条消息
manager = multiprocessing.Manager()
q = manager.Queue(5)

def fun_product():
	sleep(1)
	while True:
		info = load(filename)
		if not info:
			info = {"aa":1, "bb":2 }
			print("_1_ create new info {}".format(info))
		else:
			print("_1_ product pre info {}".format(info))
			aa = info['aa']
			bb = info['bb']
			info['aa'] = aa+2
			info['bb'] = aa+3
			print("_1_ product post info {}".format(info))

		print("_1_ save info {}".format(info))
		save(filename, info)
		#q.put(info)
		sleep(3)

def fun_get():
	while True:
		sleep(2)
		info=load(filename)
		if info:
			#print("收到消息",q.__next__().get())
			#print("q not None, but not get from it.")
			print("_1_ load info", info)
		else:
			print("_1_ load info None")

p1 = Process(target = fun_product)
p2 = Process(target = fun_get)
p1.start()
#p2.start()
p1.join()
#p2.join()
