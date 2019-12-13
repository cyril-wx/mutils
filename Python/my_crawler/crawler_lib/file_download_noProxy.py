#!/usr/bin/python
# -*- coding:utf-8 -*-
# 不经过代理的下载方法
import requests

# 1.下载小文件的话考虑的因素比较少，给了链接直接下载就好了：
_small_file_download():
	image_url = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
	r = requests.get(image_url) # create HTTP response object

	with open("python_logo.png",'wb') as f:
    		f.write(r.content)

# 2.但是如果文件比较大的话，那么下载下来的文件先放在内存中，内存还是比较有压力的。
#   所以为了防止内存不够用的现象出现，我们要想办法把下载的文件分块写到磁盘中：
_large_file_download():
	file_url = "http://codex.cs.yale.edu/avi/db-book/db4/slide-dir/ch1-2.pdf"
	r = requests.get(file_url, stream=True)

	with open("python.pdf", "wb") as pdf:
    		for chunk in r.iter_content(chunk_size=1024):
        		if chunk:
            			pdf.write(chunk)

# 3.批量文件下载的思路也很简单，首先读取网页的内容，再从网页中抽取链接信息，
#   比如通过a标签，然后再从抽取出的链接中过滤出我们想要的链接，
#   比如在本例中，我们只想下载MP4文件，那么我们可以通过文件名过滤所有链接：
archive_url = "http://www-personal.umich.edu/~csev/books/py4inf/media/"

def get_video_links():
    r = requests.get(archive_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    links = soup.findAll('a')
    video_links = [archive_url + link['href'] for link in links if link['href'].endswith('mp4')]

    return video_links


def download_video_series(video_links):
    for link in video_links:
        file_name = link.split('/')[-1]

        print("Downloading file:%s" % file_name)
        r = requests.get(link, stream=True)

        # download started
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        print("%s downloaded!\n" % file_name)


    print("All videos downloaded!")

    return


if __name__ == "__main__":
    video_links = get_video_links()
    download_video_series(video_links)