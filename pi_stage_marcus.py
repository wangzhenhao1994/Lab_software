import serial
import time
from math import floor, ceil
import numpy as np

class PI_stage:
    def __init__(self, port):
        self.ser = serial.Serial(
            port=port,
            baudrate=57600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            timeout=0.1)

    def round_to(self,num):
        return floor(num*100)/100

    def move_absolute_um(self, pos):
        self.sendcmd('MOV 1 ' + str(self.round_to(pos)))
        return 0

    def get_position_um(self):
        self.sendcmd('POS?')
        return self.get_response()

    def sendcmd(self, command):
        command = command + '\n'
        self.ser.write(command.encode('utf-8'))

    def get_response(self):
        res = self.ser.read(100).decode("utf-8")[2:]
        print(res)
        return res
    
    def setTrigWidth(self):
        self.sendcmd('TWC')
        for i in np.arange(0, 5):
            #if (i%2)==1:
            self.sendcmd('TWS 2 ' + str(i) + ' 1')
            #else:
            #    self.sendcmd('TWS 2 ' + str(i) + ' 0')
            print('TWS 2 ' + str(i) + ' 1')
            self.sendcmd('TWS 2 ' + str(i) + ' 1')
        #self.sendcmd('TWS 2 ' + str(80) + ' 0')
        #self.sendcmd('TWS 2 ' + str(81) + ' 0')
        self.sendcmd('CTO 2 3 4')

    def setSweepTime(self, t=100):
        #self.sendcmd('WTR 1 '+ str(ceil(t/1.6)) + ' 0')#adjust the period of the sweep, time = num * 0.0001 * 16000 second. 
                                                        #0.0001s is the time of every servo cycle, 16000 is the number of the point in wave table.
        self.sendcmd('WTR 1 '+ str(ceil(t/1.6)) + ' 0')

    def setCycleNum(self, n=1):
        self.sendcmd('WGC 1 '+ str(n)) # set the cycle number after initiate the wave generator

    def setWaveTable(self):
        self.sendcmd('WAV 1 X LIN 16000 100 0 16000 0 0') #create the wave table.
    
    def setWaveTableOpenLoop(self):
        self.sendcmd('WAV 1 X LIN 4000 150 0 4000 0 0') #create the wave table.

    def conWaveTable(self,n=1):
        self.sendcmd('WSL 1 '+ str(n)) # connect the wave generator to the wave table No.n

    def initWaveGen(self):
        #self.sendcmd('WSL 1 1')#Set Connection Of Wave Table To Wave Generator
        self.sendcmd('WGO 1 1')#start the wave generator
    
    def stopWaveGen(self):
        self.sendcmd('WGO 1 0')

    def setClosedLoop(self):
        self.sendcmd('SVO 1 1')

    def setOpenLoop(self):
        self.sendcmd('SVO 1 0')

    def stop(self):
        self.sendcmd('WGO 1 0')#stop the wave generator
        self.sendcmd('STP')

    def autoZero(self):
        self.sendcmd('ATZ')#stop the wave generator

    def close(self):
        self.ser.close()

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import time
   # import numpy as np
    stage = PI_stage('COM23')
    #stage.move_absolute_um(50)
    #stage.sendcmd('GWD? 1 16000 1')
    #time.sleep(3)
    #scan = stage.get_response()
    #scanline = np.fromstring(scan, sep='\n')
    #plt.plot(scanline)
    #plt.show()
    #************************************triger width setting

    ################stage.setTrigWidth() #!!!Danger!!!

    #************************************triger width setting
    #stage.move_absolute_um(50)
    #stage.setWaveTable()
    #stage.conWaveTable()
    #time.sleep(11)
    #stage.sendcmd('DRR?')
    #recordTable = stage.get_response()
    #print(recordTable)
    #stage.close()
