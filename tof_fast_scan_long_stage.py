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
from collections.abc import Iterable
from cal_ppNum import flatten
from nidaqmx_usb6229_fastscan_backup import PLLreadout_nidaqmx
from seabreeze.spectrometers import list_devices, Spectrometer
spec = Spectrometer.from_first_available()

from small_lab_gui.helper import bokeh_gui_helper as bgh
from small_lab_gui.helper import bokeh_plot_helper as bph
from small_lab_gui.helper import measurement_longstage



from shutter import Shutter
from calculate_k_b import Calibration_mass
#from read_data import FFT_ionS2
calclator = Calibration_mass(mass=[18.01528,31.99880], pixel=[824,1785])#def __init__(self, mass=[18.01528,31.99880], pixel=[2659,4575])
[k,b]=calclator.cal_k_b()
longstage = True
testing = False
fs2mm = 1/3.33564/1000

def roundTo4(num):
    return math.floor(num*10000)/10000

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
    def __init__(self, doc, running, tof_digitizer, delayer, nidaq):
        super().__init__(doc, running, tof_digitizer, delayer)
        self.title = 'Measurement'

        #digitizer
        self.dll = self.tof_digitizer.dll
        self.nDev = self.tof_digitizer.nDev

        #spectrometer
        self.spec = Spec(spec)
        #NIDAQmx
        self.nidaq_reader = nidaq

        #sum autocorrelation
        self.sumAutocorrelationPlot = bph.plot_2d()
        self.sumAutocorrelationPlot.line(legend='Sum')
        #daq readout
        self.daqReadout = bph.plot_2d()
        self.daqReadout.line(legend='Delay Monitor')

        # scan table button
        self.scanTableBtn = bokeh.models.widgets.Toggle(label='Scan Table')
        # measuement inputs
        if longstage:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [mm]', value='-101.87878')
            self.delayRange = bokeh.models.widgets.TextInput(
            title='Absolute delay range [mm]', value='0.207')#+/-1000 fs is 299.79246 um, i.e. 0.2998mm
            self.speedInput = bokeh.models.widgets.TextInput(
            title='Moving Speed [mm]', value='0.02')#0.0001 mm/s, i.e. 0.1 um/s -> 0.33356 fs is the minimum speed of the ILS250PP stage.
            self.stageStartPos = roundTo4(float(self.zeroDelInput.value)-float(self.delayRange.value))
            self.startPOS_monitor = bokeh.models.widgets.TextInput(
            title='Start Position [mm]', value=str(self.stageStartPos))
            self.ppOnlyNum = bokeh.models.widgets.TextInput(
            title='Pump/Probe-Only number', value=str(7))
        else:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [um]', value='10.')
            self.stageStartPos = bokeh.models.widgets.TextInput(
            title='Start Position [um]', value='0')

        #experiment parameter
        if longstage:
            self.sweepTimeInput = bokeh.models.widgets.TextInput(
                title='Sweep time [s]', value=str(roundTo4(2*float(self.delayRange.value)/float(self.speedInput.value))))#this value is set in the Standford delayer, here is only displayed
            
        else:
            self.sweepTimeInput = bokeh.models.widgets.TextInput(
                title='Sweep time [s]', value='120') #seconds #125 is the value before Sep. 120 is the value since 8th Sep.
            self.delay = np.arange(-1000,9000)*(100/10000)*2*3.33564*10**-15
            self.numCycle = 1 # number of cycle after initiation of the wave generator
        
        self.numSweeps = bokeh.models.widgets.TextInput(
            title='Sweep Number', value='70') # number of sweeps

        #parameters of the scan     
        # boxcar intergration time
        self.averageNum = bokeh.models.widgets.TextInput(
            title='Boxcar Average', value='5') # number of average
        self.average = int(self.averageNum.value)

        self.scanNum = 0
        self.cycles = 248000 #72000*5 correspongind t0 120.5s of measurement
        self.range = 128 # 1024 for H2O, 1536 for 2-Proponal
        self.sumSpectrum = np.zeros(self.cycles)
        # scan start time for save name
        self.now = None
        self.fname = None
        self.file = None
        self.run_time = None# this array log the runtime of each scan, which will be used to calibrate the frequency
        #record the spectrum of fiber output
        self.firstS = np.zeros(self.spec.shape)
        self.curS = np.zeros(self.spec.shape)
        self.PLLreadout_buffer = np.zeros((2000,4),dtype=float)

        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value='Reflected beam: mW\nTransmitted beam: mW\nFocus size: \nPressure: 5e-10mbar \nMeasurement time: s', rows=10)
        
        # arrange items
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.averageNum, self.numSweeps, self.zeroDelInput, self.delayRange, self.sweepTimeInput, 
            self.speedInput, self.startPOS_monitor, self.ppOnlyNum,
            self.saveBtn, self.saveNameInput,  self.scanTableBtn, self.comment, width = 200)
        self.layout = bokeh.layouts.grid([
            self.inputs,
            bokeh.layouts.column(
                self.sumAutocorrelationPlot.element, self.linePlot.element, self.daqReadout.element)
                ],
            ncols = 4)

    def start(self):

        self.ppNum=list(flatten([['pumponly','probeonly'] if i%(int(self.ppOnlyNum.value))==0 else i for i in range(1,int(self.numSweeps.value))]))
        self.totalScanNum = len(self.ppNum)
        print('\n This experiment has ' + str(self.totalScanNum) + ' sweeps.\n')
        print(self.ppNum)

        #parameters of the scan
        if longstage:
            self.parameters = 'Experiment Parameters:\n'\
            + 'Integration time (ksweeps):'+ str(self.cycles) + '\n'\
            + 'Boxcar average num:'+ str(self.average) + '\n'\
            +'Zero position of stage:' + str(self.zeroDelInput.value) + '\n'\
            +'Start Position:' + str(self.stageStartPos) + '\n'\
            +'Sweep number:' + str(self.numSweeps.value)+ '\n'\
            +'Sweep time:' + str(self.sweepTimeInput.value) +'\n'\
            +'Delay Range input(fs):' + str(self.delayRange.value) +'\n'\
            +'Speed input(fs):' + str(self.speedInput.value) +'\n'\
            +'pump/probe-only number:' + str(self.ppOnlyNum.value) +'\n'\
            +'pump/probe-only sequence:' + str(self.ppNum)
        else:
            self.parameters = 'Experiment Parameters:\n'\
            + 'Integration time (ksweeps):'+ str(self.cycles) + '\n'\
            +'Zero position of stage:' + str(self.zeroDelInput.value) + '\n'\
            +'Start Position:' + str(self.stageStartPos.value) + '\n'\
            +'Sweep number:' + str(self.numSweeps.value)
        #open shutter
        #self.shutter.set_shutter_mode(modes=['F' ,'O'])
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
                with h5py.File(self.fname + '.hdf5', 'w') as f:
                    f.create_dataset('data', compression="gzip", chunks=(1,self.range,self.cycles), shape=(int(self.totalScanNum),self.range,self.cycles))
                    f.create_dataset('spectrumLog', compression="gzip", chunks=(1,self.spec.shape), shape=(int(self.totalScanNum)//5,self.spec.shape))
                    f.create_dataset('parameters', data = self.parameters)
                    f.create_dataset('comment', data=self.comment.value, dtype=h5py.special_dtype(vlen=str))
                    f.create_dataset('ppNum', data = str(self.ppNum))
                    #self.file.create_dataset('runtime', data=self.run_time)
                    f.flush()

            except Exception as e:
                print('save error')
                print(e)
            #in future here should be able to set the phase of the wave output of wave generator
            if longstage:
                #self.delayer.set_speed_mm(10)
                self.StartPos = self.stageStartPos
                #self.delayer.move_absolute_mm(self.StartPos)#for long stage, it is important to make sure the long stage is at the start position the measurement
                self.delayer.set_speed_mm(float(self.speedInput.value))
                #self.delayer.set_backslash_mm(roundTo4(100*fs2mm))
                
                self.EndPos = float(self.zeroDelInput.value)+float(self.delayRange.value)#self.StartPos+float(self.delayRange.value)
            else:
                self.StartPos = float(self.stageStartPos.value)
                self.delayer.conWaveTable(n=1)# connect the wave generator to the wave table No.n
                self.delayer.setSweepTime(int(self.sweepTimeInput.value))
                self.delayer.setCycleNum(int(self.numCycle))#number of the cycle after initiate the wave generator

            # set running indicator to block double readout
            self.running.now_running(self)
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'

            # measurement thread
            if longstage:
                self.measurement = measurement_longstage.measurement(
                inputs=[[self.tof_digitizer.nDev,None,self.EndPos,None,None,None,None,   self.tof_digitizer.nDev,None,self.StartPos,None,None,None] for i in range(math.floor(int(self.totalScanNum)/2))],
                sequence=[
                    measurement_longstage.single_input_sequence_function(self.tof_digitizer.dll.Start),
                    measurement_longstage.sleep_function(int(3)),
                    measurement_longstage.single_input_sequence_function(self.delayer.move_absolute_mm_2),#sleep 2 second before moving
                    measurement_longstage.no_input_sequence_function(self.nidaq_reader.read),
                    measurement_longstage.sleep_function(int(5)),
                    measurement_longstage.no_input_sequence_function(self.tof_digitizer.readout_continuous),
                    measurement_longstage.sleep_function(5),
                    #due to the trigger of long stage in use is in-motion trigger, in each measurement sequence,
                    #the stage moves to the EndPOS and finish the 1st scan, then moves back and this is the 2nd scan.

                    measurement_longstage.single_input_sequence_function(self.tof_digitizer.dll.Start),
                    measurement_longstage.sleep_function(int(3)),
                    measurement_longstage.single_input_sequence_function(self.delayer.move_absolute_mm_2),
                    measurement_longstage.no_input_sequence_function(self.nidaq_reader.read),
                    measurement_longstage.sleep_function(int(5)),
                    measurement_longstage.no_input_sequence_function(self.tof_digitizer.readout_continuous),
                    ],
                update=measurement_longstage.bokeh_update_function(
                    self.update, self.doc),
                init=partial(
                    self.tof_digitizer.setup, integration=self.average),#here use averageNum replace integration time
                finish=measurement_longstage.bokeh_no_input_finish_function(
                    self.stop, self.doc),
                save_output=False)
            else:
                self.measurement = measurement_longstage.measurement(
                    inputs=[[self.tof_digitizer.nDev,None,None,None,None,self.StartPos] for i in range(int(self.numSweeps.value))],
                    sequence=[
                        measurement_longstage.single_input_sequence_function(self.tof_digitizer.dll.Start),
                        measurement_longstage.sleep_function(int(5)),
                        measurement_longstage.no_input_sequence_function(self.delayer.initWaveGen),
                        measurement_longstage.sleep_function(int(self.sweepTimeInput.value)),
                        measurement_longstage.no_input_sequence_function(self.tof_digitizer.readout_continuous),
                        measurement_longstage.single_input_sequence_function(self.delayer.move_absolute_um),
                        measurement_longstage.single_input_sequence_function(self.update)##due to the in-motion trigger of the long stage, the output need to be readout inbetween a measurement sequence
                        ],
                    update=measurement_longstage.bokeh_update_function(
                        self.update, self.doc),
                    init=partial(
                        self.tof_digitizer.setup, integration=self.average),#here use averageNum replace integration time
                    finish=measurement_longstage.bokeh_no_input_finish_function(
                        self.stop, self.doc),
                    save_output=False)
            self.measurement.start()

    def rebin(self, arr, new_shape):
        """Rebin 2D array arr to shape new_shape by averaging."""
        shape = (new_shape[0], arr.shape[0] // new_shape[0],
                new_shape[1], arr.shape[1] // new_shape[1])
        return arr.reshape(shape).mean(-1).mean(1)

    def update(self, data):

        im_data = np.transpose(np.reshape(np.array(data[5]['data'][0]), (1,self.cycles,self.range)), axes=(0,2,1))
        daq_readout = np.array(data[3]).flatten()
        #print()
        #print(daq_readout)

        curspec = np.sum(im_data[0],0)
        self.sumSpectrum = self.sumSpectrum+curspec
        # update plots
        try:
            self.linePlot.update(
                num=0, x=np.arange(curspec.size), y=curspec)
            self.sumAutocorrelationPlot.update(
                num=0, x=np.arange(curspec.size), y=self.sumSpectrum)
            self.daqReadout.update(
                num=0, x=np.arange(daq_readout.size), y = daq_readout
            )
        except Exception as e:
            print('plot error')
            print(e)
        # log pulse spectra
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
            # save data hdf5
            with h5py.File(self.fname + '.hdf5', 'r+') as f:
                f.create_dataset('daq_readout_'+str(self.scanNum), data=daq_readout, compression="gzip")
                f['data'][self.scanNum] = im_data
                if ((self.scanNum+1)%5==0 or self.scanNum==0):
                    f['spectrumLog'][self.scanNum//5] = self.curS
                f.flush()
                # save comment to separate txt file
                with open(self.fname + '.txt', 'w') as f:
                    f.write(self.comment.value)
        except Exception as e:
            print('save error')
            print(e)

        self.scanNum += 1
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
    def stop(self):
        super().stop()
        #close the shutter after the measurement
        #self.shutter.set_shutter_mode(modes=['P', 'K'])
        #self.file.close()



class shutter_gui():
    def __init__(self, doc):
        self.shutter = Shutter('COM6')
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
            self.shutter.set_shutter_mode(modes=['O', 'F'])
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
        self.shutter.set_shutter_mode(modes=['P', 'K'])
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
        nidaq = PLLreadout_nidaqmx()
        if longstage:
            stage = SMC100(1, 'COM7', silent=True)
        else:
            stage = PI_stage('COM23')

        # measurement tab
        measurementgui = tof_measurement_gui(
            doc=doc,
            running=self.running,
            tof_digitizer=digitizer,
            delayer=stage,
            nidaq=nidaq
            )

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
