import time
import serial

class Shutter():
    def __init__(self, port):

        # configure the serial connections (the parameters differs on the device you are connecting to)
        self.port = port
    
    #def set_shutter_mode(self, mode=None, modes=['P','K']):
    def set_shutter_mode(self, mode=None, modes=['P','K']):
        ser = serial.Serial(
            port=self.port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        if mode is None:
            for s in modes:  
                ser.write(s.encode())
        else:
            ser.write(mode.encode())
        ser.close()
if __name__ == '__main__':

    s = Shutter('COM4')
    # 'K'Close the shutter before fiber; 'P' Close the shutter in interferometer;
    #s.set_shutter_mode(modes=['F','O'])
    s.set_shutter_mode('F')
    #'F' open the shutter before the fiber; 'O' open the shutter in the interferometer

    #Press 'Ctrl+F5' to run
