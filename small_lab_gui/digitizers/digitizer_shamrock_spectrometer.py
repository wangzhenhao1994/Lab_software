from small_lab_gui.digitizers.digitizer import digitizer

import time
import numpy as np
from threading import Event
import small_lab_gui.digitizers.pyandor.Camera.andor as andor
import small_lab_gui.digitizers.pyandor.Spectrograph.shamrock as shamrock


class shamrock_spectrometer(digitizer):
    def __init__(self, grating=None, wavelength=None):
        self.num_sensors = 1
        try:
            self.dev = andor.Andor()
            self.dev.SetVerbose(state=False)
            self.devS = shamrock.Shamrock()
            if grating:
                self.devS.ShamrockSetGrating(grating)
                self.devS.ShamrockGetGratingInfo()
                print(self.devS.CurrGratingInfo)
            if wavelength:
                self.devS.ShamrockSetWavelength(wavelength)
            self.devS.ShamrockSetNumberPixels(1600)
            self.devS.ShamrockSetPixelWidth(16.)
            self.devS.ShamrockGetCalibration()
            self.wavelength = np.array(self.devS.wl_calibration)
            print(self.wavelength.min())
            print(self.wavelength.max())

        except Exception:
            print('couldnt find spectrometer')
        self.lastframe = 0
        self.stop_event = Event()

    def setup(self, integration, Tset=-50, cooler=False, EMCCDGain=1, PreAmpGain=0, OutputAmplifier=0):
        self.integration = integration
        self.dev.SetSingleScan()
        self.dev.SetTriggerMode(7)
        self.dev.SetShutter(1,1,0,0)
        self.dev.SetPreAmpGain(PreAmpGain)
        self.dev.SetEMCCDGain(EMCCDGain)
        # 0 = emccd
        # 1 = high nir gain
        # self.dev.SetOutputAmplifier(OutputAmplifier)
        self.dev.SetHSSpeed(OutputAmplifier, 0)
        self.dev.SetCoolerMode(1)
        # vertical binning
        self.dev.SetReadMode(0)
        self.dev.SetKineticCycleTime(0)
        self.dev.SetAcquisitionMode(1)

        if cooler:
            self.dev.SetTemperature(Tset)
            self.dev.CoolerON()
            while self.dev.GetTemperature() != 'DRV_TEMP_STABILIZED':
                print(self.dev.GetTemperature())
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
        intensities = np.flip(np.array(data))
        self.lastframe = intensities
        if (not self.stop_event.is_set()):
            return {
                'wavelength': self.wavelength,
                'intensity': intensities,
                'source': 'shamrock_spectrometer',
                'success': True}
        else:
            return {
                'wavelength': 0,
                'intensity': 0,
                'source': 'shamrock_spectrometer',
                'success': False}

    def readout_continuous(self, stop_event=Event(),
                           inp=None, init_output=None):
        self.stop_event.clear()
        self.dev.StartAcquisition()
        data = []
        self.dev.GetAcquiredData(data)
        return {
            'wavelength': self.wavelength,
            'intensity': np.flip(np.array(data)),
            'source': 'shamrock_spectrometer',
            'success': True}

    def stop(self):
        self.dev.AbortAcquisition()
        self.dev.SetShutter(1,2,0,0)
        self.stop_event.set()

    def close(self):
        print('closing shamrock spectrometer')
        self.dev.SetVerbose(state=True)
        self.dev.CoolerOFF()
        self.devS.ShamrockClose()
        self.dev.ShutDown()

