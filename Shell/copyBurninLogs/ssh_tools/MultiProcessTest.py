#!/usr/bin/python
# -*- coding:utf-8 -*-

import threading
from PanicToolPackage import getAstrisProbeID
from PanicToolPackage import getMarvinProbeID
from PanicToolPackage import readCMD
from PanicToolPackage import run_marvin

def test_astris(cycletime):
	threads = []
	for i in range(cycletime):
		t = threading.Thread(target=getAstrisProbeID,args=["30EE8C",])
		threads.append(t)
	
	for i in range(cycletime):
		threads[i].start()
	for i in range(cycletime):
		threads[i].join()
	
	print("Test Finish!")


def test_multi_process(func, cycletime, *args):
        threads = []
        for i in range(cycletime):
                t = threading.Thread(target=func,args=args)
                threads.append(t)

        for i in range(cycletime):
                threads[i].start()
        for i in range(cycletime):
                threads[i].join()

        print("Test Finish!")

if __name__ == "__main__":
#	test_multi_process(getAstrisProbeID, 20, "30EE8C")
#	test_multi_process(getMarvinProbeID, 20, "30EE8C")
#	res, rev = readCMD(["ls", "-al"], False,)
#	print res,rev

	# test run_marvin
	args = ["D42_EVT_BUILD","D42_EVT_FF","YukonNanshan16A999","Burnin","Black","3CAA","C39XXX_001"]
 	res = run_marvin("30EE8C", args)	
        print res




