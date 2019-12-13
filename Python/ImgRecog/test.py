# -*- coding:utf-8 -*-
import cv2
import numpy as np

img = cv2.imread('/Users/gdlocal1/Desktop/Cyril/Coding/Python/ImgRecog/qipan.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# cornerHarris函数图像格式为 float32 ，因此需要将图像转换 float32 类型
gray = np.float32(gray)
# cornerHarris参数：
# src - 数据类型为 float32 的输入图像。
# blockSize - 角点检测中要考虑的领域大小。
# ksize - Sobel 求导中使用的窗口大小
# k - Harris 角点检测方程中的自由参数,取值参数为 [0,04,0.06].
dst = cv2.cornerHarris(src=gray, blockSize=9, ksize=23, k=0.04)
# 变量a的阈值为0.01 * dst.max()，如果dst的图像值大于阈值，那么该图像的像素点设为True，否则为False
# 将图片每个像素点根据变量a的True和False进行赋值处理，赋值处理是将图像角点勾画出来
a = dst>0.01 * dst.max()
img[a] = [0, 0, 255]
# 显示图像
cv2.imshow('corners', img)
while (True):
#  cv2.imshow('corners', img)
  if cv2.waitKey(120) & 0xff == ord("q"):
    break
  cv2.destroyAllWindows()

