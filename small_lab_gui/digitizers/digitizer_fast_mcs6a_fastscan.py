from small_lab_gui.digitizers.digitizer import digitizer

import numpy as np
import time
from threading import Event
from small_lab_gui.company_dll.fast_mcs6a_wrapper import mcs6aDll


class mcs6a(digitizer):
    #def __init__(self, path='', cycles=248000, swpreset=5, sweepmode='1e2004'):
    def __init__(self, path='', cycles=3050, swpreset=10, sweepmode='1e2004'):
    #def __init__(self, path='', cycles=2000, swpreset=10, sweepmode='1e2000'):
    #def __init__(self, path='', cycles=590000, swpreset=1, sweepmode='1e2004'):#196.7s
        self.num_sensors = 1
        self.dll = mcs6aDll(path)
        self.nDev = 0
        self.range = 12032#1536
        #self.range = 1024 #1024 for H2O, 1536 for proponal, 128 for long stage
        self.stop_event = Event()
        self.sweepmode = sweepmode
        self.cycles = cycles #72000 corresponding to 120s
        self.swpreset = swpreset

    def setup(self, integration, timepreset=0):
        self.dll.Halt(self.nDev)
        # LSB first
        # 0x0 = 0000 is for normal mode; 0x4 = 0010 is for sequential mode
        # 0x8 = 0001 for start event generation
        # 0x2 = 0100 is tag bits off and start with rising edge
        # 0x8 = 0001 is enable start events that go to channel 4
        # 0x0 = 0000 is enable all channels
        # 0x0 = 0000 is enable all channels
        # 0x00 not important
        #self.dll.RunCmd(self.nDev, 'sweepmode=00000280')
        self.dll.RunCmd(self.nDev, 'sweepmode='+self.sweepmode)# sequential mode
        # 0x10 = 00001000 is to enable start preset,
        # sweep preset is 0x04 = 00100000, 0x1 is real time preset
        # self.dll.RunCmd(self.nDev, 'prena=10')
        self.dll.RunCmd(self.nDev, 'digio=f28')#f28 triggered by go line
        self.dll.RunCmd(self.nDev, 'prena=4')
        #parameter of sequence measurement
        self.dll.RunCmd(self.nDev, 'sequences=1')
        self.dll.RunCmd(self.nDev, 'range=' + str(int(self.range)))
        self.dll.RunCmd(self.nDev, 'swpreset='+str(self.swpreset))
        self.dll.RunCmd(self.nDev, 'cycles='+str(self.cycles))
        self.dll.RunCmd(self.nDev, 'fstchan=0')#1354 for Mass 18 and binwidth 1

        # self.dll.RunCmd(self.nDev, 'roimin=1')
        # self.dll.RunCmd(self.nDev, 'roimax=8192')
        self.integration = integration
        if timepreset:
            self.dll.RunCmd(
                self.nDev, 'rtpreset=' + str(int(self.integration)))
        else:
            self.dll.RunCmd(
                self.nDev, 'swpreset=' + str(int(self.integration)))

    def frame(self, stop_event=Event(), inp=None, init_output=None):
        self.stop_event.clear()
        # let eventual readout finish
        while ((self.dll.GetStatusData(self.nDev)['Status'].started == 3)
               and (not stop_event.is_set())
               and (not self.stop_event.is_set())):
            time.sleep(0.001)
        # stop measurement if running
        if (self.dll.GetStatusData(self.nDev)['Status'].started
           and (not stop_event.is_set())
           and (not self.stop_event.is_set())):
            self.dll.Halt(self.nDev)
            while (self.dll.GetStatusData(self.nDev)['Status'].started
                   and (not stop_event.is_set())
                   and (not self.stop_event.is_set())):
                time.sleep(0.001)
        # start acq
        self.dll.Start(self.nDev)
        # wait until acq starts
        while ((not self.dll.GetStatusData(self.nDev)['Status'].started)
               and (not stop_event.is_set())
               and (not self.stop_event.is_set())):
            time.sleep(0.001)
        # wait until acq finishes
        while (self.dll.GetStatusData(self.nDev)['Status'].started
               and (not stop_event.is_set())
               and (not self.stop_event.is_set())):
            time.sleep(0.001)
        # status such as last sweeps count and scan length
        stat = self.dll.GetStatusData(self.nDev)['Status']
        # data array
        data = np.zeros((self.num_sensors, self.range, 30000))
        for cnt in range(self.num_sensors):
            intermediate = self.dll.LVGetDat(cnt)['data']
            if data[cnt, :].size == intermediate.size:
                data[cnt, :] = intermediate
        return {'data': data,
                'sweeps': stat.cnt[self.dll.ST_SWEEPS],
                'starts': stat.cnt[self.dll.ST_STARTS],
                'runtime': stat.cnt[self.dll.ST_RUNTIME],
                'ofls': stat.cnt[self.dll.ST_OFLS],
                'totalsum': stat.cnt[self.dll.ST_TOTALSUM],
                'roisum': stat.cnt[self.dll.ST_ROISUM],
                'roirate': stat.cnt[self.dll.ST_ROIRATE],
                'source': 'fast_mcs6a',
                'success': True}

    def start_continuous(self):
        self.stop_event.clear()
        while ((self.dll.GetStatusData(self.nDev)['Status'].started == 3)
               and (not self.stop_event.is_set())):
            time.sleep(0.001)
        if (self.dll.GetStatusData(self.nDev)['Status'].started
           and (not self.stop_event.is_set())):
            self.dll.Halt(self.nDev)
            while (self.dll.GetStatusData(self.nDev)['Status'].started
                   and (not self.stop_event.is_set())):
                time.sleep(0.001)
        if not self.stop_event.is_set():
            # start acq
            # LSB first
            # 0x0 = 0000 is for normal mode
            # 0x8 = 0001 for start event generation
            # 0x2 = 0100 is tag bits off and start with rising edge
            # 0x8 = 0001 is enable start events that go to channel 4
            # 0x0 = 0000 is enable all channels
            # 0x0 = 0000 is enable all channels
            # 0x00 not important
            self.dll.RunCmd(self.nDev, 'sweepmode=00000280')
            # 0x10 = 00001000 is to enable start preset,
            # sweep preset is 0x04 = 00100000,
            #  0x1 is real time preset, 0x0 is endless
            self.dll.RunCmd(self.nDev, 'prena=0')
            self.dll.RunCmd(self.nDev, 'range=' + str(int(self.range)))
            self.dll.Start(self.nDev)
            while ((not self.dll.GetStatusData(self.nDev)['Status'].started)
                   and (not self.stop_event.is_set())):
                time.sleep(0.1)

    def readout_continuous(self, stop_event=Event(),
                           inp=None, init_output=None):
        # status such as last sweeps count and scan length
        #stat = self.dll.GetStatusData(self.nDev)['Status']
        time.sleep(3)
        # data array
        data = np.zeros((self.num_sensors, self.range*self.cycles))
        for cnt in range(self.num_sensors):
            intermediate = self.dll.LVGetDat(cnt)['data']
            #intermediate = self.dll.GetData(self.nDev)['Data']
            #np.ctypeslib.as_array(self.dll.GetData(self.nDev)['Data'],shape=(0,))
            if data[cnt, :].size == intermediate.size:
                data[cnt, :] = intermediate
        # data = self.dll.LVGetDat(0)['data']
        return data
    
    def start(self):
        self.dll.Start(self.nDev)

    def stop(self):
        self.stop_event.set()
        self.dll.Halt(self.nDev)

    def close(self):
        print('closing mcs6a')
