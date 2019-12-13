#!/usr/bin/env python

import ctypes  
so = ctypes.cdll.LoadLibrary   
lib = so("./serial_control.so")


def loginToiOS(retryTimes):
    print("Exec loginToiOS")
    lib.close_serial(1)
    print("Finish")

print
   


