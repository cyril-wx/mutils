# -*- coding:utf-8 -*-


class AInstance(object):
    '''
    被测试的单例模式类
    '''
    instance = None
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(AInstance, cls).__new__(cls, *args, **kwargs)
        return cls.instance
    def __init__(self):
        print("Init")

import threading
def task(arg):
    obj = AInstance()
    // 打印的对象都是相同的，说明创建的单例模式AInstance支持多线程
    print(obj)
for i in range(10):
    t = threading.Thread(target=task,args=[i,])
    t.start()
