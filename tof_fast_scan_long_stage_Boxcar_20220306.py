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
from nidaqmx_usb6229_fastscan2 import PLLreadout_nidaqmx
from seabreeze.spectrometers import list_devices, Spectrometer
spec = Spectrometer.from_first_available()

from small_lab_gui.helper import bokeh_gui_helper as bgh
from small_lab_gui.helper import bokeh_plot_helper as bph
from small_lab_gui.helper import measurement_longstage


from shutter import Shutter
from calculate_k_b import Calibration_mass

longstage = True
fs2mm = 1/3.33564/1000

def roundTo4(num):
    return math.floor(num*10000)/10000

from small_lab_gui.digitizers.digitizer_fast_mcs6a_fastscan import mcs6a
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

        #stage
        self.delayer = delayer
        #shutter
        self.shutter = Shutter('COM13')
        # measurement thread
        self.measurement = None
        # bokeh doc for callback
        self.doc = doc
        # global measurement running indicator
        self.running = running

        #spectrometer
        self.spec = Spec(spec)
        # spectrum plot
        self.linePlot_channel0 = bph.plot_2d()
        self.linePlot_channel0.line(legend='channel0')
        self.linePlot_channel1 = bph.plot_2d()
        self.linePlot_channel1.line(legend='channel1')
        self.linePlot_channel2 = bph.plot_2d()
        self.linePlot_channel2.line(legend='channel2')
        self.linePlot_channel3 = bph.plot_2d()
        self.linePlot_channel3.line(legend='channel3')
        self.linePlot_channel4 = bph.plot_2d()
        self.linePlot_channel4.line(legend='channel4')
        self.linePlot_ref0 = bph.plot_2d()
        self.linePlot_ref0.line(legend='ref0')
        self.linePlot_ref1 = bph.plot_2d()
        self.linePlot_ref1.line(legend='ref1')
        self.linePlot_ref2 = bph.plot_2d()
        self.linePlot_ref2.line(legend='ref2')
        self.linePlot_ref3 = bph.plot_2d()
        self.linePlot_ref3.line(legend='ref3')
        self.linePlot_ref4 = bph.plot_2d()
        self.linePlot_ref4.line(legend='ref4')

        #sum autocorrelation
        self.sumAutocorrelationPlot = bph.plot_2d()
        self.sumAutocorrelationPlot.line(legend='Sum')

        # Set up widgets
        self.startBtn = bokeh.models.widgets.Button(
            label='Start', button_type='success')
        # start thread callback
        self.startBtn.on_click(self.start)
        # scan table button
        self.scanTableBtn = bokeh.models.widgets.Toggle(label='Scan Table')

        # measuement inputs
        if longstage:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [mm]', value='-102.513')
            self.delayRange = bokeh.models.widgets.TextInput(
            title='Absolute delay range [mm]', value='300')#+/-1000 fs is 299.79246 um, i.e. 0.2998mm
            self.speedInput = bokeh.models.widgets.TextInput(
            title='Moving Speed [mm]', value='0.02')#0.0001 mm/s, i.e. 0.1 um/s -> 0.33356 fs is the minimum speed of the ILS250PP stage.
            self.stageStartPos = roundTo4(float(self.zeroDelInput.value)-0.1)
            self.startPOS_monitor = bokeh.models.widgets.TextInput(
            title='Start Position [mm]', value=str(self.stageStartPos))


        
        self.numSweeps = bokeh.models.widgets.TextInput(
            title='Sweep Number', value='1') # number of sweeps

        #parameters of the scan     

        #experiment parameter
        self.sampleRateInput = bokeh.models.widgets.TextInput(
            title='Sample Rate', value='300')
        self.averageNum = bokeh.models.widgets.TextInput(
            title='Boxcar Average', value='100') #boxcar average number
        self.average = int(self.averageNum.value)

        self.scanNum = 0
        # scan start time for save name
        self.now = None
        self.fname = None
        self.file = None
        self.run_time = None# this array log the runtime of each scan, which will be used to calibrate the frequency
        #record the spectrum of fiber output
        self.firstS = np.zeros(self.spec.shape)
        self.curS = np.zeros(self.spec.shape)
        

        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value='Reflected beam: mW\nTransmitted beam: mW\nFocus size: \nPressure: 5e-10mbar \nMeasurement time: s', rows=10)
        
        # arrange items
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.averageNum, self.sampleRateInput, self.numSweeps, self.zeroDelInput, self.delayRange,
            self.speedInput, self.startPOS_monitor, self.scanTableBtn, self.comment, width = 200)
        self.layout = bokeh.layouts.grid([
            self.inputs,
            bokeh.layouts.column(
                self.sumAutocorrelationPlot.element, self.linePlot_channel0.element, self.linePlot_channel1.element,
                 self.linePlot_channel2.element, self.linePlot_channel3.element, self.linePlot_channel4.element,self.linePlot_ref0.element,
                 self.linePlot_ref1.element, self.linePlot_ref2.element, self.linePlot_ref3.element, self.linePlot_ref4.element)
                ],
            ncols = 4)

    def start(self):
        #parameters of the scan
        if longstage:
            self.parameters = 'Experiment Parameters:\n'\
            + 'Boxcar average num:'+ str(self.average) + '\n'\
            +'Zero position of stage:' + str(self.zeroDelInput.value) + '\n'\
            +'Start Position:' + str(self.stageStartPos) + '\n'\
            +'Sweep number:' + str(self.numSweeps.value)+ '\n'\
            +'Delay Range input(fs):' + str(self.delayRange.value) +'\n'\
            +'Speed input(fs):' + str(self.speedInput.value) +'\n'

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
            if longstage:
                #self.delayer.set_speed_mm(10)
                self.StartPos = self.stageStartPos
                #self.delayer.move_absolute_mm(self.StartPos)#for long stage, it is important to make sure the long stage is at the start position the measurement
                
                #self.delayer.set_backslash_mm(roundTo4(100*fs2mm))
                self.EndPos = float(self.zeroDelInput.value)+float(self.delayRange.value)#self.StartPos+float(self.delayRange.value)
                
                #NIDAQmx
                self.sampRate = int(self.sampleRateInput.value)
                self.sweepTime=roundTo4((self.EndPos-self.StartPos)/float(self.speedInput.value)+1)
                self.nidaq_reader = PLLreadout_nidaqmx(self.sweepTime, sampRate=self.sampRate, bufferSize=self.sampRate)
                self.sumSpectrum = np.zeros((10, int(self.sampRate * self.sweepTime)))

                print('Initialize the stage!')
                self.delayer.set_speed_mm(1)
                posRan=np.round(self.delayer.get_position_mm(),5)
                print('The stage is at ' +str(posRan)+' !')
                self.delayer.move_absolute_mm_2(self.StartPos-0.05)
                time.sleep(abs(posRan-self.StartPos)+3)
                self.delayer.set_speed_mm(float(self.speedInput.value))
                self.delayer.move_absolute_mm_2(self.StartPos)
                print('The stage is at ' +str(np.round(self.delayer.get_position_mm(),5))+' !')
                time.sleep(3)
                



            # set running indicator to block double readout
            self.running.now_running(self)
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'

            # measurement thread
            if longstage:
                self.measurement = measurement_longstage.measurement(
                inputs=[[self.EndPos,None,None,   self.StartPos,None,None] for i in range(math.floor(int(self.numSweeps.value)/2))],
                sequence=[
                    measurement_longstage.single_input_sequence_function(self.delayer.move_absolute_mm_2),#sleep 2 second before moving
                    measurement_longstage.no_input_sequence_function(self.nidaq_reader.read),
                    measurement_longstage.sleep_function(int(60)),
                    #due to the trigger of long stage in use is in-motion trigger, in each measurement sequence,
                    #the stage moves to the EndPOS and finish the 1st scan, then moves back and this is the 2nd scan.


                    measurement_longstage.single_input_sequence_function(self.delayer.move_absolute_mm_2),
                    measurement_longstage.no_input_sequence_function(self.nidaq_reader.read),
                    measurement_longstage.sleep_function(int(60)),
                    ],
                update=measurement_longstage.bokeh_update_function(
                    self.update, self.doc),
                init=None,
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

        curspec = np.reshape(data[1],(11,int(self.sampRate * self.sweepTime)))
        self.sumSpectrum = self.sumSpectrum+curspec[:10]
        channel0= curspec[0]
        channel1= curspec[2]
        channel2= curspec[4]
        channel3= curspec[6]
        channel4= curspec[8]
        ref0= curspec[1]
        ref1= curspec[3]
        ref2= curspec[5]
        ref3= curspec[7]
        ref4= curspec[9]

        # update plots
        try:
            self.linePlot_channel0.update(
                num=0, x=np.arange(channel0.size), y=channel0.flatten())
            self.linePlot_channel1.update(
                num=0, x=np.arange(channel1.size), y=channel1.flatten())
            self.linePlot_channel2.update(
                num=0, x=np.arange(channel2.size), y=channel2.flatten())
            self.linePlot_channel3.update(
                num=0, x=np.arange(channel3.size), y=channel3.flatten())
            self.linePlot_channel4.update(
                num=0, x=np.arange(channel4.size), y=channel4.flatten())
            self.sumAutocorrelationPlot.update(
                num=0, x=np.arange(channel0.size), y=self.sumSpectrum[0].flatten()) #show the sum of channel0 scan
            self.linePlot_ref0.update(
                num=0, x=np.arange(ref0.size), y=ref0.flatten())
            self.linePlot_ref1.update(
                num=0, x=np.arange(ref1.size), y=ref1.flatten())
            self.linePlot_ref2.update(
                num=0, x=np.arange(ref2.size), y=ref2.flatten())
            self.linePlot_ref3.update(
                num=0, x=np.arange(ref3.size), y=ref3.flatten())
            self.linePlot_ref4.update(
                num=0, x=np.arange(ref4.size), y=ref4.flatten())
        except Exception as e:
            print('plot error')
            print(e)
        try:
            # save data hdf5, compress data due to the GB size.
            if self.scanNum == 0:
                self.file.create_dataset('data', data=curspec, compression="gzip", chunks=True, maxshape=(None,int(self.sampRate * self.sweepTime)))
                self.file.create_dataset('parameters', data = self.parameters)
                self.file.create_dataset(
                        'comment', data=self.comment.value,
                        dtype=h5py.special_dtype(vlen=str))
                self.file.flush()
            else:
                self.file['data'].resize((self.file['data'].shape[0] + 11), axis=0)
                self.file['data'][-11:] = curspec
                self.file.flush()

            # save comment to separate txt file
                with open(self.fname + '.txt', 'w') as f:
                    f.write(self.comment.value)
                    
        except Exception as e:
            print('save error')
            print(e)

        self.scanNum += 1

    def stop(self):
        if not (self.measurement is None):
            self.measurement.stop()
            self.measurement.join()
        self.running.now_stopped()
        self.startBtn.label = 'Start'
        self.startBtn.button_type = 'success'
        #close the shutter after the measurement
        self.shutter.set_shutter_mode('K')
        self.file.close()



class shutter_gui():
    def __init__(self, doc):
        self.shutter = Shutter('COM13')
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
        #self.close_list.append(measurementgui)
        self.close_list.append(shuttergui)
        self.close_list.append(stage)


print('start tof')
# start the server
bgh.bokeh_gui_helper(tof_session_handler(), 5024)
