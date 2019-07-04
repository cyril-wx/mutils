# task_worker.py
# -*- coding:utf-8 -*-
import time, queue
from multiprocessing.managers import BaseManager

# 多进程分布式例子
# 客户端：worker

# 在分布式多进程环境下，添加任务到Queue不可以直接对原始的task_queue进行操作，
# 那样就绕过了QueueManager的封装，必须通过manager.get_task_queue()获得的Queue接口添加。

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
    if not worker:
        print("worker is None, exit")

    task = worker.get_task_queue()
    result = worker.get_result_queue()
    # 从task队列取数据，并添加到result队列中

    while 1:
        try:
            n = task.get(timeout=10)
            print('worker get %d' % n)
            result.put(n)
            time.sleep(1)
        except queue.Empty:
            print("get_queue task empty")
            time.sleep(1)
            continue



if __name__ == "__main__":
	host = '127.0.0.1'
	port = 5000
	authkey = b'abc'

	# 启动worker
	worker = start_worker(host, port, authkey)
	# 获取队列
	get_queue(worker)

"""
	while 1:
		try:
			# 启动worker
			worker = start_worker(host, port, authkey)
			# 获取队列
			get_queue(worker)
		except EOFError:
			print("Server is offline. Task stopped.")
			# 是为了实现断线重连，继续任务
			continue
"""




