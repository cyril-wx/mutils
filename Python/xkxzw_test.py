#!/usr/local/bin/python3
# -*- coding:UTF-8 -*-

header={
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
'Cookie': 'ASPSESSIONIDACSSABTC=EHCDBDDBLMCNGJINEFHCAKCO; Hm_lvt_74ae19d8c337e3dfd81a041b76190ca0=1539996094,1539996188,1539996206; Hm_lpvt_74ae19d8c337e3dfd81a041b76190ca0=1539996206; ASPSESSIONIDACSRBBTD=DLPNEMFBCFKKAMGBFBBAACOD',
'Host': 'www.xkxzw.com',
'Proxy-Authorization': 'Basic RjMyMDAyNzg6Rm94Y29ubkAyMDE2',
'Proxy-Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
}

data={
'a':'123',
'b':'123',
}
url='http://www.xkxzw.com/CS123.asp'

import requests as req
import base64

#files = {'file': open('/Users/coreos/Desktop/Cyril/Python/3.txt', 'rb')}
files = {'file': open('/Users/gdlocal1/Desktop/Cyril/Coding/Python/3.txt', 'rb')}


r=req.post(url, params=data, headers=header, files=files,timeout=30)
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

print(r.headers)

