#!/usr/bin/python
# -*- coding:UTF-8 -*-
import sys

def func_1(a, b):
	print("func_1: a=%s, b=%s" %(a,b))

def func_2(a):
	print("func_2: a=%s" %a)

if __name__ == "__main__":
	module = sys.modules[__name__]
	# getattr() 函数用于返回一个对象属性值。
	# sys.argv 是获取运行python文件的时候命令行参数,且以list形式存储参数 
	# sys.argv[0] 代表当前module的名字
	func = getattr(module, sys.argv[1])
	args = None
	if len(sys.argv) > 1:
		args = sys.argv[2:]
		
	func(*args)


'''
$ python func_test.py func_1 hello world
func_1: a=hello, b=world
'''