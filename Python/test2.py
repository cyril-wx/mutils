#! coding: utf-8
# This python script is used for NonUI reboot unit, and save all syslog info
# Modify: Modified by Cyril@CoreOS on 23/07/19
# Mail: cyril.wx.jiang@mail.x.x
import serial
import subprocess
import time
import re
import os
import sys


def Port():
    Temp = subprocess.os.listdir("/dev")
    SerialPort = [line for line in Temp if "cu.kanzi" in line or "cu.usb" in line]
    if len(SerialPort) == 0:
        raise Exception("No serial device found, pls check\n没有找到串口设备，请重试")
    elif len(SerialPort) != 1:
        SerialPort = raw_input("Pls choose the Correct prot:\n%s" % ())
    else:
        SerialPort = SerialPort[0]
    return SerialPort


class DownloadData():
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        # self.data = ""
        self.index = 0
        self.SN = "NA"
        self.CFG = "NA_NA_NA"
        file("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), "w")
        self.debughandle = file("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), "a+")
        try:
            self.Device = serial.Serial(port=self.port, baudrate=self.baudrate)
            self.Device.reset_output_buffer()
            self.Device.reset_input_buffer()
        except:
            raise Exception("Sorry,Serial port init faild, pls try again\n串口初始化异常，请重试")

    def printF(self, Object):
        # print Object
        self.debughandle.write("%s" % Object)

    def Index_Init(self):
        self.index = 0

    def Read(self):
        # data_cache = None
        self.Device.flushOutput()
        error_count = 0
        while True:
            try:
                line = self.Device.readline(self.Device.inWaiting())
                yield line
            except:
                if error_count > 5: # Read() 5秒超时时间
                    self.printF("EOF: Can't read new data from device. exit.")
                    break
                time.sleep(1)
                error_count += 1
                continue
            else:
                time.sleep(0.01)
        raise EOFError("EOF: Can't read new data from device.")

    # return self.data
    def sendCmd(self, cmd):
        # debughandle = file(os.path.join(os.curdir,"debug.txt"),"a+")
        self.Device.flushInput()
        cmd = cmd + "\n"
        chunks = [cmd[i:i + 8] for i in range(0, len(cmd), 8)]
        for chunk in chunks:
            self.Device.write(chunk)
            time.sleep(0.05)
        time.sleep(0.1)


    def Login(self):
        Start = time.time()
        self.sendCmd("")
        while Start-time.time()<5:     # 5秒内未登录成功则失败
            #self.printF("********Attemping NonUI login: %s *****************" % (5 - Count))
            try:
                line = next(self.Read())
                if re.search("login:", line):
                   self.sendCmd("root")
                   line = next(self.Read())

                if re.search("Password:", line):
                    self.sendCmd("alpine")
                    self.sendCmd("")
                    line = next(self.Read())

                if re.search("root#", line):
                    print "Login successful"
                    return
                else:
                    self.sendCmd("")
                time.sleep(0.01)
            except:
                continue
        raise ValueError("Timeout: Can not Login NonUI mode, pls check the unit status")

    def TimeLine(self):
        return time.strftime("%Y-%m-%d_%H:%M:%S")

    def getFuncName(self, obj=sys._getframe()):
        """
        # 获取调用方法的方法名
        # 如：方法A调用本方法" getFuncName() "，返回 "A"
        :param obj: 无须传入参数
        :return: 调用方法的方法名
        """
        return obj.f_code.co_name

    def SN_Grab(self):
        self.sendCmd("sysconfig read -k SrNm")
        Start = time.time()
        while True and Start-time.time()<3:     # 3秒内读不到数据则失败
            try:
                line = next(self.Read())
                if re.search("Key  | Type | Data", line):
                    sn_line = next(self.Read())
                    self.SN = sn_line.strip().split("|")[2].strip()
                    return
        # print "--------------------------------->",self.SN
            except Exception as e:
                self.printF("%s.%s: %s" %(self.__class__.__name__,self.getFuncName(),e))
                break
        raise ValueError("Get SN Error.")

    def CFG_Grab(self):
        # This function still has some issues
        self.sendCmd("sysconfig read -k CFG#")
        Start = time.time()
        while True and Start - time.time() < 3:     # 3秒内读不到数据则失败
            try:
                line = next(self.Read())
                if re.search("CFG# | STR  |", line):
                    CFG = line.split("|")[2].strip().split("/")
                    self.CFG = "%s_%s_%s" % (CFG[0], CFG[-2], CFG[-1])
                    return
            except Exception as e:
                self.printF("%s.%s: %s" %(self.__class__.__name__,self.getFuncName(),e))
                break
        raise ValueError("Get CFG# Error.")

    def UpdateLogName(self):
        UpdateName = "%s/%s" % (
            os.path.dirname(sys.argv[0]), "Output/%s_%s_%s.log" % (self.SN, self.CFG, self.TimeLine()))
        os.rename("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), UpdateName)



if __name__ == '__main__':
    SerialPort = Port()
    Dev = DownloadData('%s/%s' % ("/dev", SerialPort), 115200)

    Dev.sendCmd("")
    #   while True:
    #       Dev.sendCmd("")
    #       time.sleep(0.5)
    #       print(next(Dev.Read()))

    Dev.Login()
    Dev.SN_Grab()
    Dev.CFG_Grab()
    print Dev.SN


    Count = 0
    while Count < 50:
        Count = Count + 1
        Dev.sendCmd("")
        Dev.Login()
        Dev.sendCmd("#reboot ********%s_reboot**********" % (Count))
        Dev.printF("#reboot ******** %s reboot **********"%(Count))
        time.sleep(0.1)
        # Dev.sendCmd("")
        # Use cold boot instead reboot
        # Dev.sendCmd("reboot")


        # command to shut down the unit by putting unit into shipping mode.

        Dev.sendCmd("smcif -r CHI1")
        Dev.sendCmd("smcif -w CHI1 0")
        Dev.sendCmd("smcif -r CHI1")
        Dev.sendCmd("smcif -smbWritePEC 2 0x16 0xC5 2 0x0E 0x55")

        time.sleep(0.1)
        Start = time.time()
        while True:
            line = next(Dev.Read())
            if re.search("tx_flush:", line):
                Start = time.time()
                Dev.sendCmd("")
            if re.search("login:", line):
                break
            if (time.time()-Start > 45):
                Dev.printF("Timeout: Can't go into iOS mode.")
                exit (1)
            time.sleep(0.01)
            continue

    Dev.UpdateLogName()

