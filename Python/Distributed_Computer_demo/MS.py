# server.py
# -*- coding:utf-8 -*-

# 多进程分布式Demo
# Server and Client
# master服务端原理：通过managers模块把Queue通过网络暴露出去，其他机器的进程就可以访问Queue了
# 服务进程负责启动Queue，把Queue注册到网络上，然后往Queue里面写入任务，代码如下:

import sys
from multiprocessing.managers import BaseManager
import time
from jc import utils
from SqliteTools import SqliteHelper
import json

try:        ## Python2/Python3 兼容设置
    import queue
except:
    import Queue as queue


# Master工站IP
master_IP = "127.0.0.1"
# master_PORT
master_PORT = None
# Slave工站IP
slave_IP = []
# 集群内所有工站IP
all_IP = None
# 认证密钥，master和slave必须统一
authKey=None
# 数据库文件（路径）
SQLiteDB=None
# 数据库存储Panic data的表名
DBTableName=None


class Server(object):
    # 初始化自定义logger
    mlog = utils.my_logger("Server")

    # 发送任务的队列 - 最多1000个数据
    task_queue = queue.Queue(1000)
    # 接收结果的队列 - 最多1000个数据
    result_queue = queue.Queue(1000)
    # 由master管理的共享data 列表
    share_data = []

    # 使用标准函数来代替lambda函数，避免python2.7中，pickle无法序列化lambda的问题
    def get_task_queue(self):
        global task_queue
        return task_queue

    # 使用标准函数来代替lambda函数，避免python2.7中，pickle无法序列化lambda的问题
    def get_result_queue(self):
        #global result_queue
        return self.result_queue

    # 使用标准函数来代替lambda函数，避免python2.7中，pickle无法序列化lambda的问题
    def get_share_data(self):
        #global share_data
        return self.share_data

    def startManager(self, host, port, authkey):
        # 把两个Queue都注册到网络上，callable参数关联了Queue对象，注意回调函数不能使用括号
        BaseManager.register('get_task_queue', callable=self.get_task_queue)
        BaseManager.register('get_result_queue', callable=self.get_result_queue)
        BaseManager.register('get_share_data', callable=self.get_share_data)
        # 设置host,绑定端口port，设置验证码为authkey
        manager = BaseManager(address=(host, port), authkey=authkey)
        # 启动manager服务器
        manager.start()
        return manager

    def put_data(self, manager, obj):
        # 通过网络访问share_data
        data = manager.get_share_data()
        data.append(obj)

    def get_data(self, worker):
        # 通过网络访问share_data
        result = worker.get_share_data()
        return result

    def get_result(self, worker):
        # 通过网络访问queueu
        result = worker.get_result_queue()
        try:
            time.sleep(0.1)
            n = result.get(timeout=5)
            self.mlog.info("Result get {}".format(n))
            return n
        except queue.Empty:
            self.mlog.info("get_result result empty...")
            return None
        else:
            pass



class Client(object):
    # 初始化自定义logger
    mlog = utils.my_logger("Client")

    def start_worker(self, host, port, authkey):
        # 由于这个BaseManager只从网络上获取queue，所以注册时只提供名字
        BaseManager.register('get_task_queue')
        BaseManager.register('get_result_queue')
        BaseManager.register('get_share_data')
        self.mlog.info('Connecting to server %s' % host)
        # 注意，端口port和验证码authkey必须和manager服务器设置的完全一致
        worker = BaseManager(address=(host, port), authkey=authkey)
        # 链接到manager服务器
        try:
            worker.connect()
        except Exception as e:
            self.mlog.exception(e)
            self.mlog.info("Connect to server failed...")

            exit(255)
        else:
            self.mlog.info('Server %s connected.' % host)
            return worker

    def put_queue(self, manager, objs):
        # 通过网络访问queueu
        task = manager.get_result_queue()
        for obj in objs:
            try:
                # print("Put obj:{}".format(obj))
                self.mlog.info("Put obj:{}".format(obj))
                task.put(obj)
                time.sleep(0.5)
            except queue.Full:
                self.mlog.info("put_queue task full.exit ")
                break

	# 使用标准函数来代替lambda函数，避免python2.7中，pickle无法序列化lambda的问题
	def get_share_data(self):
		#global share_data
		return self.share_data

	def put_data(self, worker, obj):
		# 通过网络访问share_data
		data = worker.get_share_data()
		data.append(obj)

	def get_data(self, worker):
		# 通过网络访问share_data
		result = worker.get_share_data()
		return result


def test_slave(jFile, data={}):
    # 加载配置文件app_config.json
    loadConfigData(jFile)

    # 实例化一个Slave
    slave = Client()
    # 获取本机IP
    #localhost = str(os.system("ifconfig en0 | tail -n4 | head -n1 | awk -F ' ' '{print $2}'")).strip()
    # 启动worker
    worker = slave.start_worker(master_IP, master_PORT, authKey)
    if worker:
        result = worker.get_result_queue()
        if result:
            print("slave put data: {}".format(data))
            result.put(data)

def test_master(jFile):
    """
    # 测试调用master。master作为server端，是无限循环处于监听状态中。
    """
    # 加载配置文件app_config.json
    loadConfigData(jFile)

    # 实例化一个Master
    master = Server()
    # 启动manager服务器
    manager = master.startManager(master_IP, master_PORT, authKey)

    # 给task队列添加数据
    # data = range(0, 20)
    # put_queue(manager, data)
    # get_queue(manager)

    # 发送与接收共享data
    #master.put_data(manager, "123")
    #print(master.get_data(manager))

    dbHelper = SqliteHelper(SQLiteDB)

    while True:
        # 为了节约master主机资源，这里可以延时接收数据
        time.sleep(10)
        try:
            # 接收数据
            data = master.get_result(manager)
            if data != None:
                # 将数据录入sqlite数据库
                dbHelper.insert(data, table=DBTableName)

        except Exception as e:
            print(e)
            exit(1)
    
    # 关闭服务器
    # manager.shutdown


def loadConfigData(jFile="/Users/gdlocal1/Desktop/Cyril/Coding/Panic4.1/AutoPanic/AutoPanic/JsonConfig/app_config.json"):

    try:
        with open(jFile, "r") as f:
            data = json.load(f, encoding="utf-8")

            global slave_IP, master_IP, all_IP, authKey, master_PORT, SQLiteDB, DBTableName
            slave_IP = list(data["Cluster"]["slave_IP"])
            master_IP = str(data["Cluster"]["master_IP"])
            all_IP = slave_IP.append(master_IP)
            master_PORT = int(data["Cluster"]["master_PORT"])
            authKey = str(data["Cluster"]["authKey"])
            SQLiteDB = str(data["Cluster"]["SQLiteDB"])
            DBTableName = str(data["Cluster"]["DBTableName"])

    except ValueError:
        print("JSON 格式错误，请检查。")
        print("提示1：请参照前面已有数据格式")
        print("提示2：最后一个Value后必须不能有逗号")
        exit(1)
    else:
        print("JSON 格式正确，可以放心使用。")
    # exit(0)


if __name__ == "__main__":
    #test_master()
    module = sys.modules[__name__]

    argv = None
    if len(sys.argv) > 2:
        func = getattr(module, sys.argv[1])
        argv = sys.argv[2:]
        func(*argv)
    else:
        print("Usage: python ./Cluster.py <FuncName> <AppConfig.json_PATH> <*args>.")
        exit(1)

    """
    # 测试共享data 列表
	# put_data(manager, "123")
	print(slave.get_data(worker))
    """