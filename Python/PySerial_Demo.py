#! coding: utf-8
# This python script is used for NonUI reboot unit, and save all syslog info
# Modify: Modified by Cyril@CoreOS on 23/07/19
# Mail: cyril.wx.jiang@mail.x.x
#! coding: utf-8
# This python script is used for NonUI reboot unit, and save all syslog info
#
#
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
        self.data = ""
        self.index = 0
        self.SN = "NA"
        self.CFG = "NA_NA_NA"
        file("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), "w")
        self.debughandle = file("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), "a+")
        try:
            self.Device = serial.Serial(port=self.port, baudrate=self.baudrate)
            self.Device.reset_output_buffer()
            self.Device.reset_input_buffer()
        # help(self.Device)
        except:
            raise Exception("Sorry,Serial port init faild, pls try again\n串口初始化异常，请重试")

    def printF(self, Object):
        print Object
        self.debughandle.write(self.data)

    def Index_Init(self):
        self.index = 0

    def Read(self):
        self.data = ""
        ## Modified by Cyril - 07/24D BEGIN
        self.Device.flushOutput()
        ## Modified by Cyril - 07/24D END
        while True:
            temp = self.Device.readline(self.Device.inWaiting())

            ## Modified by Cyril - 07/23D BEGIN
            self.data = "%s%s" % (self.data, temp)
            ## Modified by Cyril - 07/23D END

            time.sleep(0.005)
            if not bool(temp):
                self.index = self.index + 1
                ## Modified by Cyril - 07/23D BEGIN
                time.sleep(1)
                ## Modified by Cyril - 07/23D END
            else:
                self.Index_Init()
            if self.index == 3:
                self.Index_Init()
                if bool(self.data):
                    self.printF(self.data)
                break

    # return self.data
    def sendCmd(self, cmd):
        # debughandle = file(os.path.join(os.curdir,"debug.txt"),"a+")
        self.data =""
        ## Modified by Cyril - 07/24D BEGIN
        self.Device.flushInput()
        ## Modified by Cyril - 07/24D END
        cmd = cmd + "\n"
        chunks = [cmd[i:i + 8] for i in range(0, len(cmd), 8)]
        for chunk in chunks:
            self.Device.write(chunk)
            time.sleep(0.05)
        time.sleep(0.1)
        self.Read()

    def Login(self):

        Count = 5

        while Count:
            self.printF("********Attemping NonUI login: %s *****************" % (5 - Count))
            self.sendCmd("")
            ## Modified by Cyril - 07/24D BEGIN
            if re.search("login:", self.data.replace("\n","")):
                self.sendCmd("root")
                if re.search("Password:", self.data.replace("\n","")):
                    self.sendCmd("alpine")
                if re.search("root#", self.data.replace("\n","")):
                    print "Login successful"
                    break
            elif re.search("root#", self.data.replace("\n","")):
                print "Alread in NonUI root mode"
                break
            ## Modified by Cyril - 07/24D END
            Count = Count - 1
            if not bool(Count):
                raise ValueError("Can not Login NonUI mode, pls check the unit status")

    def SN_Grab(self):
        self.sendCmd("sysconfig read -k SrNm")
        # print self.data
        try:
            SN = [line.split()[-1] for line in self.data.split("\n") if "SrNm |" in line][-1]
            self.SN = SN
        # print "--------------------------------->",self.SN
        except Exception, e:
            print "Wrong SN type, pls call DRI "

    def CFG_Grab(self):
        # This function still has some issues
        self.sendCmd("sysconfig read -k CFG#")
        CFG = [line.split()[-1].split("/") for line in self.data.split("\n") if "CFG# |" in line][-1]
        try:
            self.CFG = "%s_%s_%s" % (CFG[0], CFG[-2], CFG[-1])
        except Exception, e:
            CFG = "NA_NA_NA"

    def TimeLine(self):
        return time.strftime("%Y-%m-%d_%H-%M-%S")

    def UpdateLogName(self):
        UpdateName = "%s/%s" % (
        os.path.dirname(sys.argv[0]), "Output/%s_%s_%s.log" % (self.SN, self.CFG, self.TimeLine()))
        os.rename("%s/%s" % (os.path.dirname(sys.argv[0]), "Output/debug.log"), UpdateName)


if __name__ == '__main__':

    SerialPort = Port()
    Dev = DownloadData('%s/%s' % ("/dev", SerialPort), 115200)
    Dev.sendCmd("")
    Dev.Login()
    Dev.SN_Grab()
    Dev.CFG_Grab()
    print Dev.SN
    print Dev.CFG
#    exit(0)

    Count = 0
    while Count < 50:
        Count = Count + 1
        Dev.sendCmd("")
        Dev.Login()
        Dev.sendCmd("#reboot ********%s_reboot**********" % (Count))
        # Dev.printF("#reboot ******** %s reboot **********"%(Count))
        time.sleep(0.1)
        # Dev.sendCmd("")
        # Use cold boot instead reboot
        # Dev.sendCmd("reboot")

        # command to shut down the unit by putting unit into shipping mode.
        Dev.sendCmd("smcif -r CHI1")
        Dev.sendCmd("smcif -w CHI1 0")
        Dev.sendCmd("smcif -r CHI1")
        Dev.sendCmd("sleep 2")
        Dev.sendCmd("smcif -smbWritePEC 2 0x16 0xC5 2 0x0E 0x55")

        time.sleep(0.1)
        Start = time.time()
        while True:
            Dev.Read()

            ## Modified by Cyril - 07/23D BEGIN
            if re.search("tx_flush:", Dev.data):
                Dev.sendCmd("")
                Dev.Read()
                if re.search("login:", Dev.data):
                    break
            ## Modified by Cyril - 07/23D	END

            if time.time() - Start > 45:
                break
    Dev.UpdateLogName()
