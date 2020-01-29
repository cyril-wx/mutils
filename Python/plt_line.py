# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
from functools import reduce
import numpy as np

tlist = {}

with open("./npi_sw.csv", 'r', encoding="utf-8") as f:
	t1 = f.readline()
	t2 = f.readline()
	t3 = f.readline()
	for line in f.readlines():
		try:
			name = line.split(",")[1].strip()
			x = []
			for i in line.split(",")[3:]:
				try:
					x.append(float(i))
				except Exception as e:
					#print(e)
					pass
		except Exception as e:
			#print(e)
			continue
		tlist[name] = x

		#print ("{}: {}".format(name, x))



def showAll():
	for people in list(tlist.keys())[:10]:
		y = tlist[people]
		x = [i for i in range(1, len(y)+1)]
		plt.plot(x, y)

	for i in range(len(x)):
		#if  (i & 1) != 0:
		if i % 2 == 0:
			drawColLine(i, (35, 40))

	plt.show()


def showPerson(name):
	y = tlist[name]
	x = [i for i in range(1, len(y) + 1)]
	plt.plot(x, y)

	for i in range(len(x)):
		#if  (i & 1) != 0:
		if i % 2 == 0:
			drawColLine(i, (35, 40))

	plt.show()

def drawColLine(x=1, y=(-1, 1)):
	Y = np.linspace(y[0], y[1], 12)
	X = np.ones(Y.size)
	# plot
	plt.plot((0 + x) * X, Y, linewidth=1, color='blue')
	#plt.show()

#drawColLine(10, (-10, 10))

#showPerson("蔣維熙")

showAll()
