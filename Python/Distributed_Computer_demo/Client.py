#task_worker.py
# -*- coding:utf-8 -*-

# 多进程分布式例子
# 客户端：worker

# 在分布式多进程环境下，添加任务到Queue不可以直接对原始的task_queue进行操作，
# 那样就绕过了QueueManager的封装，必须通过manager.get_task_queue()获得的Queue接口添加。

# encoding:utf-8

import random, time, queue
from multiprocessing.managers import BaseManager


def start_worker(host, port, authkey):
	# 由于这个BaseManager只从网络上获取queue，所以注册时只提供名字
	BaseManager.register('get_task_queue')
	BaseManager.register('get_result_queue')
	print ('Connect to server %s' % host)
	# 注意，端口port和验证码authkey必须和manager服务器设置的完全一致
	worker = BaseManager(address=(host, port), authkey=authkey)
	# 链接到manager服务器
	try:
		worker.connect()
	except Exception as e:
		print(e)
		print("Tring reconnection...")
		time.sleep(1)
		start_worker(host, port, authkey)
	else:
		print('Connecting server %s' % host)
		return worker


def get_queue(worker):
	task = worker.get_task_queue()
	result = worker.get_result_queue()
	# 从task队列取数据，并添加到result队列中
	while 1:
		if task.empty():
			time.sleep(1)
			continue
		n = task.get(timeout=1)
		print ('worker get %d' % n)
		result.put(n)
		time.sleep(1)

if __name__ == "__main__":
	host = '127.0.0.1'
	port = 5000
	authkey = b'abc'

	# 启动worker
	worker = None

	# while & if 是为了实现断线重连，继续任务
	while not worker:
		# 启动worker
		worker = start_worker(host, port, authkey)
		if worker:
			try:
				# 获取队列
				get_queue(worker)
			except EOFError:
				print("Server is offline. Task stopped.")
				worker = None
				continue
		else:
			print("retry get worker...")
			continue
