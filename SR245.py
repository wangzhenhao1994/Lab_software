from lib2to3.pytree import convert
import serial
from serial.threaded import ReaderThread, Protocol, LineReader
import select
import time
from math import floor, ceil
import numpy as np
import sys

from sympy import re

def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] >> shift) & 0x1

class SR245:
    def __init__(self, port):
        self.ser = serial.Serial(
            port=port,
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            timeout=1)
        self.stop = 0

    def round_to(self,num):
        return floor(num*100)/100

    def sendcmd(self, command):
        command = command + '\r'
        self.ser.write(command.encode('utf-8'))

    def setAllPortsRead(self):
        self.sendcmd('I8')

    def setTrigEveryN_B1(self, N):
        self.sendcmd('T'+str(N))
    
    def setAsyMode(self):
        self.sendcmd('MA')
    
    def setSyMode(self):
        self.sendcmd('MS')

    def readAllChannel(self):
        self.sendcmd('X')
        self.get_response()

    def get_response(self):
        res = self.ser.read(1000000).decode("utf-8")
        #print(res)
        return res
    
    def getSSBit_response(self,num):
        inter = []
        data = []
        timeout = 30
        #read,_,_ = select.select([self.ser], [], [], timeout)
        #inter = self.ser.read(60000)
        self.sendcmd('X')
        #print(self.ser.read(self.ser.in_waiting).decode('utf-8'))
        inter.append(self.ser.readline())

        #print(inter)
        inter=[item for sublist in inter for item in sublist]
        inter_res=[str(access_bit(inter,i)) for i in range(len(inter)*8)]
        res_bit=''.join(inter_res)
        inter2=[res_bit[i:i+16] for i in range(0, len(res_bit), 16)]
        if inter2[-1:] == ['1111111111111111']:
            inter2 = inter2[:-1]
            self.stop = 1
        else:
            print('Read Error!')
        for point in inter2:
            point = point[:8][::-1]+point[-8:][::-1]
            #print(point)
            if point[3]=='0':
                data.append(int(point[-12:],2)*0.0025)
                #print(int(point[-12:],2)*0.0025)
            else:
                data.append(-int(point[-12:],2)*0.0025)
                #print(-int(point[-12:],2)*0.0025)
        #data=[int(point[:8][::-1]+point[-8:][::-1],2)*0.0025 if point[3]=='0' else -int(point[:8][::-1]+point[-8:][::-1],2)*0.0025 for point in inter2]
        #data=[int(point[-12:],2)*0.0025 if point[3]=='0' else -int(point[-12:],2)*0.0025 for point in inter2]
        #print(np.reshape(data,(num,5)))
        #return(data)
        return np.sum(np.reshape(data,(num,5)),axis=0)/num

    def getSS_response(self, num):
        res=[]
        for i in range(num):
            self.sendcmd('N')
            res.append(self.get_response())
        print(len(res))
        return res
    
    def readSSBit(self,num):
        self.sendcmd('SC1,2,3,4,5:'+str(num))
        time.sleep(100/3000*(num+1))


    def close(self):
        self.ser.close()

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import time
    import numpy as np
    converter = SR245('COM8')
    converter.sendcmd('MR')
    converter.setAllPortsRead()
    converter.setAsyMode()
    #converter.setSyMode()
    converter.setTrigEveryN_B1(100)
    
    
    
    #time.sleep(1)
    print(converter.readSSBit(10))
    #converter.sendcmd('X')
    #print(converter.getSSBit_response(20))
    #print(converter.getSS_response(5))
    print(converter.getSSBit_response(10))
    
    
    