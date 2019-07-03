#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
from multiprocessing import Process, Pipe
import time
import os

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
save(filename, q)

def fun1():
	sleep(1)
	aa = bb = 1
	while True:
		aa = aa + 1
		bb = bb + 2
		info = {"2_a":aa,"2_b":bb}
		print("_2_ put info {}".format(info))
		q.put(info)
		save(filename, q)
		sleep(3)

def fun2():
	sleep(2)
	while True:
		q=load(filename)
		if q:
			#print("收到消息",q.__next__().get())
			print("_2_ 收到消息", q.get())

p1 = Process(target = fun1)
p2 = Process(target = fun2)
p1.start()
p2.start()
p1.join()
p2.join()
