#!/usr/bin/env python3
import requests


headers = {}
#写入User Agent信息
headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
headers['User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'
headers['Host'] = 'tv.efoxconn.com'
headers['Referer']='http://tv.efoxconn.com/Video/'


proxies = {}
#proxies['http']='http://F3200278:Foxconn%402016@10.191.131.43:3128'
#proxies['https']='http://F3200278:Foxconn%402016@10.191.131.43:3128'
proxies['http']="http://10.134.149.69:80"

from requests.auth import HTTPBasicAuth
pwd="\u0043\u0079\u0072\u0069\u006c\u0032\u0030\u0031\u0038\u0031\u0030"
auth = HTTPBasicAuth('dpbg%5CF1235027', pwd)

#url="http://tv.efoxconn.com/upload/20180420/131686640831406250.mp4"
url
r=requests.post(url, headers=headers)
#r=requests.post("http://tv.efoxconn.com/Home/Result?k=%E4%B9%9D%E5%B7%9E%C2%B7%E6%B5%B7%E4%B8%8A%E7%89%A7%E4%BA%91%E8%AE%B0", headers=headers, proxies=proxies)
print("Status_Code:",r.status_code)
print("Headers:",headers)
