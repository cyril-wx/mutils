#!/usr/local/bin/python3
# -*- coding:UTF-8 -*-


'''
data={
'a':'123',
'b':'123',
}
'''
url="http://localhost:8080/codetest"

import requests as req
import base64

files = {'file': open('/Users/gdlocal1/Desktop/Cyril/Coding/Python/3.txt', 'rb')}


r=req.get(url,timeout=30)
print(r.status_code)
print("=====================")
print("r.tyep->:",type(r.text))
print("r.encoding->:",r.encoding)
print("r.apparent_encoding->:",r.apparent_encoding)
print("r.content->: ",r.content)
print("r.text->: ",r.text)
print("b64encode->: ",base64.urlsafe_b64encode(r.content))
#res_data=base64.urlsafe_b64encode(r.content)

info=r.content.decode("gb2312")
print("utf-8/gb2312/ decode:Info-> ",info)

#info2=r.content.decode()
#print("default decode:Info2->",info2)

#print(r.content)

