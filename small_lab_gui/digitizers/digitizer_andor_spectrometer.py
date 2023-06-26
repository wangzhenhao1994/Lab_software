from small_lab_gui.digitizers.digitizer import digitizer

import time
import numpy as np
from threading import Event
import small_lab_gui.digitizers.pyandor.Camera.andor as andor


class andor_spectrometer(digitizer):
    def __init__(self):
        self.num_sensors = 1
        try:
            self.dev = andor.Andor()
            self.dev.SetVerbose(state=False)
        except Exception:
            print('couldnt find spectrometer')
        self.lastframe = 0
        self.stop_event = Event()

    def setup(self, integration, Tset=-70, cooler=False, EMCCDGain=1, PreAmpGain=0):
        self.integration = integration
        self.dev.SetSingleScan()
        self.dev.SetTriggerMode(0)
        self.dev.SetShutter(1,1,0,0)
        self.dev.SetPreAmpGain(PreAmpGain)
        self.dev.SetEMCCDGain(EMCCDGain)
        self.dev.SetCoolerMode(1)
        # vertical binning
        self.dev.SetReadMode(0)
        self.dev.SetKineticCycleTime(0)
        self.dev.SetAcquisitionMode(1)

        if cooler:
            self.dev.SetTemperature(Tset)
            self.dev.CoolerON()
            while self.dev.GetTemperature() is not 'DRV_TEMP_STABILIZED':
                print("Temperature is: %g [Set T: %g]" % (self.dev.temperature, Tset))
                time.sleep(10)
        else:
            self.dev.CoolerOFF()
        
        self.dev.SetExposureTime(integration/1000)
        time.sleep(integration/1000.*2)
        self.dev.StartAcquisition()


    def frame(self, stop_event=Event(), inp=None, init_output=None):
        self.stop_event.clear()
        self.dev.StartAcquisition()
        data = []
        self.dev.GetAcquiredData(data)
        intensities = np.array(data)
        self.lastframe = intensities
        if (not self.stop_event.is_set()):
            return {
                'wavelength': np.linspace(0, 1, len(intensities)),
                'intensity': intensities,
                'source': 'andor_spectrometer',
                'success': True}
        else:
            return {
                'wavelength': 0,
                'intensity': 0,
                'source': 'andor_spectrometer',
                'success': False}

    def readout_continuous(self, stop_event=Event(),
                           inp=None, init_output=None):
        self.stop_event.clear()
        self.dev.StartAcquisition()
        data = []
        self.dev.GetAcquiredData(data)
        return {
            'wavelength': np.linspace(0, 1, len(data)),
            'intensity': np.array(data),
            'source': 'andor_spectrometer',
            'success': True}

    def stop(self):
        self.dev.AbortAcquisition()
        self.dev.SetShutter(1,2,0,0)
        self.stop_event.set()

    def close(self):
        print('closing andor spectrometer')
        self.dev.ShutDown()

