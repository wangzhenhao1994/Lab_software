# implement a nkt superk select controller
from small_lab_gui.axes.linear_axis import linear_axis_controller
from small_lab_gui.axes.linear_axis import linear_axis

import small_lab_gui.axes.nkt.NKTP_DLL as nkt
#import nkt.NKTP_DLL as nkt

import numpy as np

class linear_axis_controller_nkt():
    num_axes = 0

    def __init__(self, port=None):
            self.port = port

    def reinit(self):
        pass

    def command(self, command):
        pass

    def readline(self):
        pass

    def stop(self):
        pass

    def close(self):
        print('closing jena eda4 com port')
        closeResult = nkt.closePorts('')
        print('Close result: ', nkt.PortResultTypes(closeResult))


class linear_axis_nkt_select():
    def __init__(self, controller, addr=18):
        self.controller = controller
        self.addr = addr
        self.referenced = True
        self.tol_um = 0.001
        print(nkt.NKTPDLL)

    def reinit(self):
        pass

    def rf_on(self):
        result = nkt.registerWriteU8(self.controller.port, 16, 0x30, 1, -1)
        print('Setting rf on', nkt.RegisterResultTypes(result))

    def rf_off(self):
        result = nkt.registerWriteU8(self.controller.port, 16, 0x30, 0, -1)
        print('Setting rf off', nkt.RegisterResultTypes(result))

    def abs_move(self, aim_position, power=None, linearize=True):
        self.aim_position = aim_position
        self.reinit()
        result = nkt.registerWriteU32(self.controller.port, 16, 0x90, int(aim_position*1000), -1)
        print('Setting select wavelength 1', nkt.RegisterResultTypes(result))
        if power:
            # input from 0 to 1
            result = nkt.registerWriteU16(self.controller.port, 16, 0xB0, int(aim_position*1000), -1)
            print('Setting select power 1', nkt.RegisterResultTypes(result))
        # this is so far no measured but done by eye!
        elif linearize:
            #     1 at 450
            #                                            0.2 at 700
            if aim_position < 533.:
                lin = 1
            elif aim_position > 560.:
                lin = 0.07
            else:
                lin = 1. - (0.5-0.5*np.cos((aim_position-533.)/(560.-533.)*np.pi)) * (1.-0.07)
            result = nkt.registerWriteU16(self.controller.port, 16, 0xB0, int(lin*1000), -1)
            print('Setting select power 1', nkt.RegisterResultTypes(result))


    def follow_move(self, stop_event=None, inp=None, init_output=None):
        # doesnt really make sense
        self.position = nkt.registerReadU32(self.controller.port, 16, 0x90, -1)/1000
        if (self.position - self.aim_position)**2 < self.tol_um**2:
            stop_event.set()
        return self.position

    def get_position(self):
        self.position = nkt.registerReadU32(self.controller.port, 16, 0x90, -1)[1]/1000
        return self.position

    def stop(self):
        pass

    def home(self):
        pass

    def zero(self):
        pass

class linear_axis_nkt_varia(linear_axis_nkt_select):

    """def rf_on(self):
        result = nkt.registerWriteU8(self.controller.port, 16, 0x30, 1, -1)
        print('Setting rf on', nkt.RegisterResultTypes(result))

    def rf_off(self):
        result = nkt.registerWriteU8(self.controller.port, 16, 0x30, 0, -1)
        print('Setting rf off', nkt.RegisterResultTypes(result))"""

    def abs_move(self, aim_position, power=None, linearize=True):
        self.aim_position = aim_position
        
        result = nkt.registerWriteU16(self.controller.port, 16, 0x33, int((aim_position+5)*10), -1)
        _, res  = nkt.registerReadU16(self.controller.port, 16, 0x66, -1)
        while res & (1<<13):
            print(res)
            _, res  = nkt.registerReadU16(self.controller.port, 16, 0x66, -1)

        result = nkt.registerWriteU16(self.controller.port, 16, 0x34, int((aim_position-5)*10), -1)
        _, res  = nkt.registerReadU16(self.controller.port, 16, 0x66, -1)
        while res & (1<<14):
            print(res)
            _, res  = nkt.registerReadU16(self.controller.port, 16, 0x66, -1)

        print('Setting select wavelength 1', nkt.RegisterResultTypes(result))
        if power:
            # input from 0 to 1
            result = nkt.registerWriteU16(self.controller.port, 15, 0x37, int(power*10), -1)
            print('Setting select power 1', nkt.RegisterResultTypes(result))
        # this is so far no measured but done by eye!
        elif linearize:
            #     1 at 450
            #                                            0.2 at 700
            if aim_position < 650:
                lin = 0.5
                if (aim_position < 570) and (aim_position > 470):
                    lin = 0.35
            elif aim_position > 730.:
                lin = 0.12
            else:
                lin = 0.5 - (aim_position-650.)/(730.-650.) * (0.5-0.12)
            result = nkt.registerWriteU16(self.controller.port, 15, 0x37, int(lin*1000), -1)

            print('Setting select power 1', nkt.RegisterResultTypes(result))
        elif 1:
            result = nkt.registerWriteU16(self.controller.port, 15, 0x37, int(0.3*1000), -1)
            print('Setting select power 1', nkt.RegisterResultTypes(result))
        else: 
            pass


    def follow_move(self, stop_event=None, inp=None, init_output=None):
        # doesnt really make sense
        # this is still wrong bc second output is the outpu
        self.position = (
            nkt.registerReadU16(self.controller.port, 16, 0x33, -1)/10
            +nkt.registerReadU16(self.controller.port, 16, 0x34, -1)/10)/2
        return self.position

    def get_position(self):
        # this is still wrong bc second output is the outpu
        self.position = (
            nkt.registerReadU16(self.controller.port, 16, 0x33, -1)/10
            +nkt.registerReadU16(self.controller.port, 16, 0x34, -1)/10)/2
        return self.position



if __name__ == '__main__':
    c = linear_axis_controller_nkt(port='COM4')
    s = linear_axis_nkt_select(controller=c)
    s.abs_move(600.014)
    print(s.get_position())