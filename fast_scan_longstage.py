from numpy.core.fromnumeric import shape
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
from nidaqmx_usb6229_fastscan2 import PLLreadout_nidaqmx
from cal_ppNum import flatten
spec = Spectrometer.from_first_available()

from small_lab_gui.helper import bokeh_gui_helper as bgh
from small_lab_gui.helper import bokeh_plot_helper as bph
from small_lab_gui.helper import measurement

def roundTo4(num):
    return math.floor(num*10000)/10000

from shutter import Shutter
from calculate_k_b import Calibration_mass
#from read_data import FFT_ionS2
calclator = Calibration_mass(mass=[18.01528,31.99880], pixel=[824,1785])#def __init__(self, mass=[18.01528,31.99880], pixel=[2659,4575])
[k,b]=calclator.cal_k_b()


from smc100pp import SMC100

from small_lab_gui.helper.postToELOG import elog
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

class tof_measurement_gui():
    def __init__(self, doc, running, delayer):
        self.title = 'Measurement'

        #spectrometer
        self.spec = Spec(spec)
        #stage
        self.delayer = delayer
        #shutter
        #self.shutter = Shutter('COM22')
        # measurement thread
        self.measurement = None
        # bokeh doc for callback
        self.doc = doc
        # global measurement running indicator
        self.running = running


        # spectrum plot
        self.linePlot = bph.plot_2d()
        self.linePlot.line(legend='Current')
        #sum autocorrelation
        self.sumAutocorrelationPlot = bph.plot_2d()
        self.sumAutocorrelationPlot.line(legend='Sum')

        # Set up widgets
        self.startBtn = bokeh.models.widgets.Button(
            label='Start', button_type='success')

        # save button
        self.saveBtn = bokeh.models.widgets.Button(
            label='Save Spectrum', button_type='success')
        self.saveBtn.on_click(self.save_spectrum)
        self.saveNameInput = bokeh.models.widgets.TextInput(
            title='Legend Name', value='Name')

        # start thread callback
        self.startBtn.on_click(self.start)


        # scan table button
        self.scanTableBtn = bokeh.models.widgets.Toggle(label='Scan Table')
        # measuement inputs

        self.zeroDelInput = bokeh.models.widgets.TextInput(
        title='Zero Delay [mm]', value='-101.87878')
        self.zeroShiftInput = bokeh.models.widgets.TextInput(
        title='Zero shift [mm]', value='0.01')
        self.delayRange = bokeh.models.widgets.TextInput(
        title='Absolute delay range [mm]', value='0.6')#+/-1000 fs is 299.79246 um, i.e. 0.2998mm
        self.speedInput = bokeh.models.widgets.TextInput(
        title='Moving Speed [mm]', value='0.02')#0.0001 mm/s, i.e. 0.1 um/s -> 0.33356 fs is the minimum speed of the ILS250PP stage.
        self.stageStartPos = roundTo4(float(self.zeroDelInput.value)-float(self.delayRange.value)+float(self.zeroShiftInput.value))
        self.startPOS_monitor = bokeh.models.widgets.TextInput(
        title='Start Position [mm]', value=str(self.stageStartPos))
        self.ppOnlyNum = bokeh.models.widgets.TextInput(
        title='Pump/Probe-Only number', value=str(7))
                #experiment parameter
        self.sweepTimeInput = bokeh.models.widgets.TextInput(
            title='Integration time [s]', value='20') #seconds
        self.sampleRateInput = bokeh.models.widgets.TextInput(
                title='Sample Rate', value='1000')
        
        self.numCycle = 1 # number of cycle after initiation of the wave generator
        self.numSweeps = bokeh.models.widgets.TextInput(
            title='Sweep Number', value='30') # number of sweeps
        self.ppOnlyNum = bokeh.models.widgets.TextInput(
            title='Pump/Probe-Only number', value=str(10))

        self.averageNum = bokeh.models.widgets.TextInput(
            title='Boxcar Average', value='100') # number of average

        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value='Reflected beam: mW\nTransmitted beam: mW\nFocus size: \nPressure: 5e-10mbar\nTime: 116.7ss\nStandford delay: 0.5s,119s', rows=10)

        # arrange items
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.averageNum, self.numSweeps, self.zeroDelInput, self.delayRange, self.sweepTimeInput, 
            self.speedInput, self.startPOS_monitor, self.ppOnlyNum,
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
        
        # scan start time for save name
        self.now = None
        self.fname = None
        self.file = None
        self.run_time = None# this array log the runtime of each scan, which will be used to calibrate the frequency
        #record the spectrum of fiber output
        self.firstS = np.zeros(self.spec.shape)
        self.curS = np.zeros(self.spec.shape)

    def start(self):
        
        self.ppNum=list(flatten([['pumponly','probeonly'] if i%(int(self.ppOnlyNum.value))==0 else i for i in range(1,int(self.numSweeps.value))]))
        self.totalScanNum = len(self.ppNum)
        print('\n This experiment has ' + str(self.totalScanNum) + ' sweeps.\n')

        #container of the data from daq
        self.sampRate = int(self.sampleRateInput.value)
        self.sumSpectrum = np.zeros(self.sampRate * int(self.sweepTimeInput.value))

        #prepare the long stage
        self.delay = np.arange(self.sampRate * int(self.sweepTimeInput.value))*float(self.delayRange.value)*1000*2*3.33564*10**-15
        self.delayer.set_speed_mm(0.5)
        self.StartPos = self.stageStartPos
        self.delayer.move_absolute_mm(self.StartPos)#for long stage, it is important to make sure the long stage is at the start position the measurement
        self.EndPos = float(self.zeroDelInput.value)+float(self.zeroShiftInput.value)#self.StartPos+float(self.delayRange.value)

        #NIDAQmx
        self.nidaq_reader = PLLreadout_nidaqmx(int(self.sweepTimeInput.value), sampRate=self.sampRate, bufferSize=self.sampRate)

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

            # set running indicator to block double readout
            self.running.now_running(self)
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'

            #parameters of the scan
            self.parameters = 'Experiment Parameters:\n'\
            +'Boxcar average num:'+ str(self.averageNum.value) + '\n'\
            +'Sample Rate:'+ str(self.sampRate) + '\n'\
            +'SRS delay generator:'+ str('A=0.3,B=0.1') + '\n'\
            +'Zero position of stage:' + str(self.zeroDelInput.value) + '\n'\
            +'Start Position:' + str(self.stageStartPos) + '\n'\
            +'Sweep number:' + str(self.numSweeps.value)+ '\n'\
            +'Sweep time:' + str(self.sweepTimeInput.value) +'\n'\
            +'Delay Range input(fs):' + str(self.delayRange.value) +'\n'\
            +'Speed input(fs):' + str(self.speedInput.value) +'\n'\
            +'pump/probe-only number:' + str(self.ppOnlyNum.value) +'\n'\
            +'pump/probe-only sequence:' + str(self.ppNum)
            # integration time

            self.run_time = np.zeros(int(self.numSweeps.value))
            # measurement thread
            self.measurement = measurement.measurement(
                inputs=[[float(self.speedInput.value),self.EndPos,None,None,0.5,self.StartPos,None] for i in range(int(self.totalScanNum))],
                sequence=[
                    measurement.single_input_sequence_function(self.delayer.set_speed_mm),
                    measurement.single_input_sequence_function(self.delayer.move_absolute_mm_2),
                    measurement.no_input_sequence_function(self.nidaq_reader.read),
                    measurement.sleep_function(int(2)),
                    measurement.single_input_sequence_function(self.delayer.set_speed_mm),
                    measurement.single_input_sequence_function(self.delayer.move_absolute_mm_2),
                    measurement.sleep_function(int(3))
                    ],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=None,#here use averageNum replace integration time
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
        curspec = np.reshape(data[2],(1,self.sampRate * int(self.sweepTimeInput.value)))
        self.sumSpectrum = self.sumSpectrum+curspec

        # update plots
        try:
            self.linePlot.update(
                num=0, x=np.arange(curspec.size), y=curspec.flatten())
            self.sumAutocorrelationPlot.update(
                num=0, x=np.arange(curspec.size), y=self.sumSpectrum.flatten())
        except Exception as e:
            print('plot error')
            print(e)

        try:
            if self.scanNum == 0:
                self.firstS=self.spec.updateSpectra()
                self.curS = self.spec.updateSpectra()
            elif ((self.scanNum+1)%5==0):
                self.curS = self.spec.updateSpectra()
        except Exception as e:
            print('Spectrometer is gone!!!')
            print(e)
        # save scan every step
        try:
            # save data hdf5, compress data due to the GB size.
            if self.scanNum == 0:
                self.file.create_dataset('data', data=curspec, compression="gzip", chunks=True, maxshape=(None,self.sampRate * int(self.sweepTimeInput.value)))
                self.file.create_dataset('spectrumLog', data=self.curS, compression="gzip", chunks=True, maxshape=(None,self.spec.shape))
                #self.file.create_dataset('runtime', data=self.run_time)
                self.file.create_dataset('parameters', data = self.parameters)
                self.file.create_dataset('ppNum', data = str(self.ppNum))
                self.file.create_dataset(
                        'comment', data=self.comment.value,
                        dtype=h5py.special_dtype(vlen=str))
                self.file.flush()
            else:
                self.file['data'].resize((self.file['data'].shape[0] + 1), axis=0)
                self.file['data'][-1] = curspec
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

        #if self.ppNum[self.scanNum]=='pumponly':
        #    try:
        #        print('\n Now begin to measure pump-only spectra!')
        #        self.shutter.set_shutter_mode('U')
        #    except Exception as e:
        #        print('shutter error')
        #        print(e)
        #elif self.ppNum[self.scanNum]=='probeonly':
        #    try:
        #        print('\n Now begin to measure probe-only spectra!')
        #        self.shutter.set_shutter_mode('R')
        #    except Exception as e:
        #        print('shutter error')
        #        print(e)
        #else:
        #    try:
        #        print('\n This is the No.' + str(self.ppNum[self.scanNum]) + ' sweep.')
        #        self.shutter.set_shutter_mode('O')
        #    except Exception as e:
        #        print('shutter error')
        #        print(e)
        self.scanNum += 1

    def save_spectrum(self):
        self.linePlot.save_current(name=self.saveNameInput.value, num=0)

        
    def stop(self):
        if not (self.measurement is None):
            self.measurement.stop()
            self.measurement.join()
        self.running.now_stopped()
        self.startBtn.label = 'Start'
        self.startBtn.button_type = 'success'
        #close the shutter after the measurement
        #self.shutter.set_shutter_mode(modes=['K','P'])
        self.file.close()
    
    def close(self):
        self.shutter.set_shutter_mode(modes=['K','P'])
        self.file.close()


class shutter_gui():
    def __init__(self, doc):
        self.shutter = Shutter('COM22')
        self.title = 'Shutter'
        # bokeh doc for callback
        self.doc = doc

        self.width = 150
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
            self.shutter.set_shutter_mode(modes=['F', 'O'])
            # switch start to stop button
            self.openBtn.label = 'Close All'
            self.openBtn.button_type = 'danger'
            self.openFiberBtn.button_type = 'danger'
        else:
            self.closeAll()

    def openFiber(self):
        if self.openFiberBtn.label == 'Open Fiber':
            self.shutter.set_shutter_mode(mode='F')
            self.openFiberBtn.label = 'Close Fiber'
            self.openFiberBtn.button_type = 'danger'
            self.openBtn.button_type = 'success'
        else:
            self.closeFiber()

    def closeAll(self):
        self.shutter.set_shutter_mode(modes=['K', 'P'])
        self.openBtn.label = 'Open All'
        self.openBtn.button_type = 'success'
        self.openFiberBtn.button_type = 'success'


    def closeFiber(self):
        self.shutter.set_shutter_mode(mode='K')
        self.openFiberBtn.label = 'Open Fiber'
        self.openFiberBtn.button_type = 'success'
        self.openBtn.button_type = 'success'

    def close(self):
        self.closeAll()

class tof_session_handler(bgh.bokeh_gui_session_handler):
    def open_session(self, doc):
        self.running = bgh.running()
        # hardware
        stage = SMC100(1, 'COM7', silent=True)

        # measurement tab
        measurementgui = tof_measurement_gui(
            doc=doc,
            running=self.running,
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


print('start tof')
# start the server
bgh.bokeh_gui_helper(tof_session_handler(), 5024)
