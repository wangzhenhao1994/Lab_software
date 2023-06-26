from numpy.core.fromnumeric import shape
from small_lab_gui.digitizers.digitizer import digitizer
from bokeh.layouts import column
import numpy as np
from functools import partial
import os
import datetime
import matplotlib.pyplot as plt
import h5py
import math
import bokeh
import time
from seabreeze.spectrometers import list_devices, Spectrometer
spec = Spectrometer.from_first_available()

from small_lab_gui.helper import bokeh_gui_helper as bgh
from small_lab_gui.helper import bokeh_plot_helper as bph
from small_lab_gui.helper import measurement



from shutter import Shutter
from calculate_k_b import Calibration_mass
#from read_data import FFT_ionS2
calclator = Calibration_mass(mass=[18.01528,31.99880], pixel=[824,1785])#def __init__(self, mass=[18.01528,31.99880], pixel=[2659,4575])
[k,b]=calclator.cal_k_b()

longstage = False
testing = False
if not testing:
    # for the lab
    from small_lab_gui.digitizers.digitizer_fast_mcs6a_fastscan import mcs6a
    if longstage:
        from smc100pp import SMC100
    else:
        from pi_stage import PI_stage
    from small_lab_gui.helper.postToELOG import elog
else:
    # for testing
    from small_lab_gui.digitizers.digitizer_fast_mcs6a_dummy import mcs6a_dummy \
        as mcs6a
    from small_lab_gui.axes.linear_axis_dummy import linear_axis_controller_dummy \
        as linear_axis_controller_jena_eda4
    from small_lab_gui.axes.linear_axis_dummy import linear_axis_dummy \
        as linear_axis_piezojena_eda4
    from small_lab_gui.helper.postToELOG_dummy import elog_dummy as elog
from tof_backup_20210502 import tof_alignment_gui

class Spec(object):
    # a wrapper for the spectrometer

    def __init__(self, spec):
        self.spec = spec
        self.wavelength = self.spec.wavelengths()
        self.shape = self.wavelength.shape[0]

    def updateSpectra(self):
        self.spec.integration_time_micros(200000)
        return np.reshape(np.array(self.spec.intensities(),dtype='float64'),(1,2048))

class tof_measurement_gui(tof_alignment_gui):
    def __init__(self, doc, running, tof_digitizer, delayer, logbook = None):
        super().__init__(doc, running, tof_digitizer, delayer)
        self.logbook = logbook
        self.title = 'Measurement'

        #digitizer
        self.dll = self.tof_digitizer.dll
        self.nDev = self.tof_digitizer.nDev

        #spectrometer
        self.spec = Spec(spec)

        #sum autocorrelation
        self.sumAutocorrelationPlot = bph.plot_2d()
        self.sumAutocorrelationPlot.line(legend='Sum')

        # scan table button
        self.scanTableBtn = bokeh.models.widgets.Toggle(label='Scan Table')
        # measuement inputs
        if longstage:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [mm]', value='11.3503')
        else:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [um]', value='10.')


        self.stageStartPos = bokeh.models.widgets.TextInput(
                title='Start Position [um]', value='0')
                #experiment parameter
        self.sweepTimeInput = bokeh.models.widgets.TextInput(
            title='Integration time [s]', value='120') #seconds #125 is the value before Sep. 120 is the value since 8th Sep.
        self.delay = np.arange(-1000,9000)*(100/10000)*2*3.33564*10**-15
        self.numCycle = 1 # number of cycle after initiation of the wave generator
        self.numSweeps = bokeh.models.widgets.TextInput(
            title='Sweep Number', value='30') # number of sweeps

        self.averageNum = bokeh.models.widgets.TextInput(
            title='Boxcar Average', value='5') # number of average

        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value='Reflected beam: mW\nTransmitted beam: mW\nFocus size: \nPressure: 5e-10mbar', rows=10)

        # arrange items
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.averageNum, self.numSweeps, self.zeroDelInput, self.stageStartPos,
            self.sweepTimeInput,
            self.saveBtn, self.saveNameInput,  self.scanTableBtn, self.comment, width = 200)
        self.layout = bokeh.layouts.grid([
            self.inputs,
            bokeh.layouts.column(
                self.sumAutocorrelationPlot.element, self.linePlot.element)
                ],
            ncols = 4)
        self.parameters = None#saved parameters
        
        #parameters of the scan
        self.scanNum = 0
        self.cycles = 70000 #72000 correspongind t0 120.5s of measurement
        self.range = 1024 # 1024 for H2O, 1536 for 2-Proponal
        self.sumSpectrum = np.zeros(self.cycles)
        # scan start time for save name
        self.now = None
        self.fname = None
        self.file = None
        self.run_time = None# this array log the runtime of each scan, which will be used to calibrate the frequency
        #record the spectrum of fiber output
        self.firstS = np.zeros(self.spec.shape)
        self.curS = np.zeros(self.spec.shape)

    def start(self):

        #open shutter
        #self.shutter.set_shutter_mode(modes=['F','O'])
        #time to start the measurement
        self.now = datetime.datetime.now()
        # in case this measurement is running, stop it
        if self.running.am_i_running(self):
            self.stop()
        # in case a different measurement is running, do nothing
        elif self.running.is_running():
            pass
        else:

            try:
                os.makedirs(
                    self.now.strftime('%Y-%m') + '/'
                    + self.now.strftime('%Y-%m-%d'), exist_ok=True)
                self.fname = (self.now.strftime('%Y-%m') + '/'
                        + self.now.strftime('%Y-%m-%d')
                        + '/scan_tof_'
                        + self.now.strftime('%Y-%m-%d-%H-%M-%S'))
                self.file = h5py.File(self.fname + '.hdf5', 'w')
            except Exception as e:
                print('save error')
                print(e)
            #in future here should be able to set the phase of the wave output of wave generator
            self.delayer.conWaveTable(n=1)# connect the wave generator to the wave table No.n
            self.delayer.setSweepTime(int(self.sweepTimeInput.value))
            self.delayer.setCycleNum(int(self.numCycle))#number of the cycle after initiate the wave generator

            # set running indicator to block double readout
            self.running.now_running(self)
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'
            #parameters of the scan
            self.parameters = 'Experiment Parameters:\n'\
            + 'Integration time (ksweeps):'+ str(self.integrationInput.value) + '\n'\
            +'Zero position of stage:' + str(self.zeroDelInput.value) + '\n'\
            +'Start Position:' + str(self.stageStartPos.value) + '\n'\
            +'Sweep number:' + str(self.numSweeps.value)
            # integration time
            self.average = int(self.averageNum.value)

            self.StartPos = float(self.stageStartPos.value)

            self.run_time = np.zeros(int(self.numSweeps.value))
            # measurement thread
            self.measurement = measurement.measurement(
                inputs=[[self.tof_digitizer.nDev,None,None,None,None,self.StartPos] for i in range(int(self.numSweeps.value))],
                sequence=[
                    measurement.single_input_sequence_function(self.tof_digitizer.dll.Start),
                    measurement.sleep_function(int(5)),
                    measurement.no_input_sequence_function(self.delayer.initWaveGen),
                    measurement.sleep_function(int(self.sweepTimeInput.value)),
                    measurement.no_input_sequence_function(self.tof_digitizer.readout_continuous),
                    measurement.single_input_sequence_function(self.delayer.move_absolute_um)
                    ],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=partial(
                    self.tof_digitizer.setup, integration=self.average),#here use averageNum replace integration time
                finish=measurement.bokeh_no_input_finish_function(
                    self.stop, self.doc),
                save_output=False)
            self.measurement.start()

    def rebin(self, arr, new_shape):
        """Rebin 2D array arr to shape new_shape by averaging."""
        shape = (new_shape[0], arr.shape[0] // new_shape[0],
                new_shape[1], arr.shape[1] // new_shape[1])
        return arr.reshape(shape).mean(-1).mean(1)

    def update(self, data):
        im_data = np.transpose(np.reshape(np.array(data[4]['data'][0]), (self.cycles,self.range)))
        #self.run_time[self.scanNum] = np.array(data[4]['runtime'])
        #print(self.run_time)
        curspec = np.sum(im_data,0)
        #print(np.sum(curspec))
        self.sumSpectrum = self.sumSpectrum+curspec

        # update plots
        try:
            self.linePlot.update(
                num=0, x=np.arange(curspec.size), y=curspec)
            self.sumAutocorrelationPlot.update(
                num=0, x=np.arange(curspec.size), y=self.sumSpectrum)
        except Exception as e:
            print('plot error')
            print(e)

        try:
            self.delayer.move_absolute_um(0)
            if self.scanNum == 0:
                self.firstS=self.spec.updateSpectra()
                self.curS = self.spec.updateSpectra()
            elif ((self.scanNum+1)%5==0):
                self.curS = self.spec.updateSpectra()
        except Exception as e:
            print('Spectrometer is gone!!!')
            print(e)
        # save scan every step
        print('This is the No.' + str(self.scanNum) + ' sweep.')
        try:
            # save data hdf5, compress data due to the GB size.
            if self.scanNum == 0:
                self.file.create_dataset('data', data=im_data, compression="gzip", chunks=True, maxshape=(None,self.cycles))
                self.file.create_dataset('spectrumLog', data=self.curS, compression="gzip", chunks=True, maxshape=(None,self.spec.shape))
                #self.file.create_dataset('runtime', data=self.run_time)
                self.file.create_dataset('parameters', data = self.parameters)
                self.file.create_dataset(
                        'comment', data=self.comment.value,
                        dtype=h5py.special_dtype(vlen=str))
                self.file.flush()
            else:
                self.file['data'].resize((self.file['data'].shape[0] + im_data.shape[0]), axis=0)
                self.file['data'][-im_data.shape[0]:] = im_data
                if ((self.scanNum+1)%5==0 or self.scanNum==0):
                    self.file['spectrumLog'].resize((self.file['spectrumLog'].shape[0] + 1), axis=0)
                    self.file['spectrumLog'][-1] = self.curS
                self.file.flush()

            # save comment to separate txt file
                with open(self.fname + '.txt', 'w') as f:
                    f.write(self.comment.value)
                    
        except Exception as e:
            print('save error')
            print(e)
        self.scanNum += 1
    def stop(self):
        super().stop()
        #close the shutter after the measurement
        #self.shutter.set_shutter_mode(modes=['K','P'])
        #self.file.close()



class shutter_gui():
    def __init__(self, doc):
        self.shutter = Shutter('COM9')
        self.title = 'Shutter'
        # bokeh doc for callback
        self.doc = doc

        self.width = 300
        self.height = round(0.618*self.width)
        self.openBtn = bokeh.models.widgets.Button(
            label='Open All', button_type='success', width=self.width, height=self.height)
        self.openFiberBtn = bokeh.models.widgets.Button(
            label='Open Fiber', button_type='success', width=self.width, height=self.height)
        # start thread callback
        self.openBtn.on_click(self.openAll)
        self.openFiberBtn.on_click(self.openFiber)

        self.layout = bokeh.layouts.row(self.openBtn, self.openFiberBtn, width=1600, height=400)

    
    def openAll(self):
        if self.openBtn.label == 'Open All':
            #self.shutter.set_shutter_mode(modes=['F', 'O'])
            # switch start to stop button
            self.openBtn.label = 'Close All'
            self.openBtn.button_type = 'danger'
            self.openFiberBtn.button_type = 'danger'
        else:
            self.closeAll()

    def openFiber(self):
        if self.openFiberBtn.label == 'Open Fiber':
            #self.shutter.set_shutter_mode(mode='F')
            self.openFiberBtn.label = 'Close Fiber'
            self.openFiberBtn.button_type = 'danger'
            self.openBtn.button_type = 'success'
        else:
            self.closeFiber()

    def closeAll(self):
        #self.shutter.set_shutter_mode(modes=['K', 'P'])
        self.openBtn.label = 'Open All'
        self.openBtn.button_type = 'success'
        self.openFiberBtn.button_type = 'success'


    def closeFiber(self):
        #self.shutter.set_shutter_mode(mode='K')
        self.openFiberBtn.label = 'Open Fiber'
        self.openFiberBtn.button_type = 'success'
        self.openBtn.button_type = 'success'

    def close(self):
        self.closeAll()

class tof_session_handler(bgh.bokeh_gui_session_handler):
    def open_session(self, doc):
        self.running = bgh.running()
        # hardware
        digitizer = mcs6a(sweepmode='1e2004')
        if longstage:
            stage = SMC100(1, 'COM22', silent=True)
        else:
            stage = PI_stage('COM23')

        # measurement tab
        measurementgui = tof_measurement_gui(
            doc=doc,
            running=self.running,
            tof_digitizer=digitizer,
            delayer=stage)

        shuttergui = shutter_gui(doc=doc)

        self.title = 'TOF Readout'
        self.tabs = [
            {'layout': measurementgui.layout, 'title': measurementgui.title},
            {'layout': shuttergui.layout, 'title': shuttergui.title}]

        # this list is auto-closed, all close functions of the
        # added objects are called at session destruction
        self.close_list.append(measurementgui)
        self.close_list.append(shuttergui)
        self.close_list.append(stage)
        self.close_list.append(digitizer)


print('start tof')
# start the server
bgh.bokeh_gui_helper(tof_session_handler(), 5024)
