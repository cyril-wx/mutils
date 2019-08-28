#!/usr/bin/python
# -*- coding:utf-8 -*-

try:    # Python2 需导入
	## izip比zip在处理大列表时更快
	from itertools import izip as zip
except Exception as e:
	print(e)


try:        # python3 需导入
	from functools import reduce  # python3 需导入，python2 内建
except Exception as e:
	print(e)


name = ["张三", "李四", "王五", "李六"]  # 保存名字列表
sign = ["白羊座", "双鱼座", "狮子座", "处女座"]  #保存星座列表

# zip & unzip
zipper = zip(name,sign)
unzipper=zip(*zipper)
for i in unzipper:
	print(i)

# zip & dict
print(dict(zip(name, sign)))

# map & reduce
mapper = map( lambda x,y: {x:y}, name, sign)
reducer = reduce( lambda x,y: dict(x, **y), list(mapper))
print (reducer)
