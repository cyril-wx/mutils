#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib2

response = urllib2.urlopen("http://image.baidu.com")
print response.read()

