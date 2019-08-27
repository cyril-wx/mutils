# client.py
# -*- coding:utf-8 -*-

# 在分布式多进程环境下，添加任务到Queue不可以直接对原始的task_queue进行操作，
# 那样就绕过了QueueManager的封装，必须通过manager.get_task_queue()获得的Queue接口添加。

import random, Queue as queue
import time
from multiprocessing.managers import BaseManager
from jc import utils

# 初始化自定义logger
mlog = utils.my_logger("Client")

cal_queue = queue.Queue(3)

def start_worker(host, port, authkey):
	# 由于这个BaseManager只从网络上获取queue，所以注册时只提供名字
	BaseManager.register('get_task_queue')
	BaseManager.register('get_result_queue')
	mlog.info ('Connect to server %s' % host)
	# 注意，端口port和验证码authkey必须和manager服务器设置的完全一致
	worker = BaseManager(address=(host, port), authkey=authkey)
	# 链接到manager服务器
	try:
		worker.connect()
	except Exception as e:
		mlog.exception(e)
		mlog.info("Tring reconnection...")
		time.sleep(1)
		start_worker(host, port, authkey)
	else:
		mlog.info('Connecting server %s' % host)
		return worker

def get_queue(worker):
	if not worker:
		mlog.info("worker is None, exit")

	task = worker.get_task_queue()
	result = worker.get_result_queue()
	# 从task队列取数据，并添加到result队列中

	tag = 0
	while 1:
		tag = tag + 1
		time.sleep(1)
		if cal_queue.full() or (tag>3 and not cal_queue.empty()):
			cal_sum = 0
			while not cal_queue.empty():
				cal_sum += cal_queue.get()
			result.put(cal_sum)
			mlog.info('result put %d' % cal_sum)
			tag = 0
		try:
			n = task.get(timeout=10)
			mlog.info('worker get %d' % n)
			cal_queue.put(n)
		except queue.Empty:
			mlog.info("get_queue task empty...retring")
			continue
		except queue.Full:
			mlog.info("put_cal_queue task full...waiting")
			continue



if __name__ == "__main__":
	host = '127.0.0.1'
	port = 5000
	authkey = b'abc'

	# 启动worker
	worker = start_worker(host, port, authkey)
	# 获取队列
	get_queue(worker)
