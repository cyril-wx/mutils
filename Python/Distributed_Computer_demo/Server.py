# task_manager.py
# -*- coding:utf-8 -*-

# 多进程分布式Demo
# 服务器端
# master服务端原理：通过managers模块把Queue通过网络暴露出去，其他机器的进程就可以访问Queue了
# 服务进程负责启动Queue，把Queue注册到网络上，然后往Queue里面写入任务，代码如下:

import random, queue
from multiprocessing.managers import BaseManager
import numpy as np
import time


# 发送任务的队列
task_queue = queue.Queue()
# 接收结果的队列
result_queue = queue.Queue()


# 使用标准函数来代替lambda函数，避免python2.7中，pickle无法序列化lambda的问题
def get_task_queue():
	global task_queue
	return task_queue


# 使用标准函数来代替lambda函数，避免python2.7中，pickle无法序列化lambda的问题
def get_result_queue():
	global task_queue
	return task_queue


def startManager(host, port, authkey):
    # 把两个Queue都注册到网络上，callable参数关联了Queue对象，注意回调函数不能使用括号
    BaseManager.register('get_task_queue', callable=get_task_queue)
    BaseManager.register('get_result_queue', callable=get_result_queue)
    # 设置host,绑定端口port，设置验证码为authkey
    manager = BaseManager(address=(host, port), authkey=authkey)
    # 启动manager服务器
    manager.start()
    return manager


def put_queue(manager, objs):
	# 通过网络访问queueu
	task = manager.get_task_queue()
	for obj in objs:
		try:
			print("Put obj:{}".format(obj))
			task.put(obj)
			time.sleep(1)
		except queue.Full:
			print("put_queue task full.exit ")
			break



def get_result(worker):
	result = worker.get_result_queue()
	while 1:
		try:
			n = result.get(timeout=10)
			print("Result get {}".format(n))
			time.sleep(1)
		except queue.Empty:
			print("get_result result empty...retring")
			continue
		else:
			pass




if __name__ == "__main__":

    host = '127.0.0.1'
    port = 5000
    authkey = b'abc'
    # 启动manager服务器
    manager = startManager(host, port, authkey)

    # 数据
    data = np.arange(0,20)

    # 给task队列添加数据
    put_queue(manager, data)
    #get_queue(manager)

    get_result(manager)

    # 关闭服务器
    manager.shutdown


