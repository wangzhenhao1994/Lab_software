from nidaqmx._task_modules.channels.channel import Channel
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
longstage = False
if longstage:
    from smc100pp import SMC100
else:
    from pi_stage import PI_stage

from tof_backup_20210502 import tof_alignment_gui
from small_lab_gui.digitizers.digitizer_fast_mcs6a_fastscan import mcs6a
if longstage:
    from smc100pp import SMC100
else:
    from pi_stage import PI_stage
from nidaqmx_usb6229_fastscan_asyn import PLLreadout_nidaqmx
from cal_ppNum import flatten


from small_lab_gui.helper import bokeh_gui_helper as bgh
from small_lab_gui.helper import bokeh_plot_helper as bph
from small_lab_gui.helper import measurement
from tof_backup_20210502 import tof_alignment_gui


from shutter import Shutter
from calculate_k_b import Calibration_mass
#from read_data import FFT_ionS2
calclator = Calibration_mass(mass=[18.01528,31.99880], pixel=[824,1785])#def __init__(self, mass=[18.01528,31.99880], pixel=[2659,4575])
[k,b]=calclator.cal_k_b()

class tof_measurement_gui(tof_alignment_gui):
    def __init__(self, doc, running, tof_digitizer, delayer, logbook = None):
        super().__init__(doc, running, tof_digitizer, delayer)
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
        #digitizer
        self.dll = self.tof_digitizer.dll
        self.nDev = self.tof_digitizer.nDev


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
        self.linePlot_channel5 = bph.plot_2d()
        self.linePlot_channel5.line(legend='channel5')#reference channel to channel 1
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

        #sum autocorrelation boxcar
        self.sumAutocorrelationPlot = bph.plot_2d()
        self.sumAutocorrelationPlot.line(legend='Sum')

        #sum autocorrelation digitizer
        self.sumAutocorrelationPlotD = bph.plot_2d()
        self.sumAutocorrelationPlotD.line(legend='SumD')

        # Set up widgets
        self.startBtn = bokeh.models.widgets.Button(
            label='Start', button_type='success')
        self.integrationInput = bokeh.models.widgets.TextInput(
            title='Integration time [ksweeps]', value='6')
        self.stagePos = bokeh.models.widgets.TextInput(
            title='Stage Position [um]', value='50.')
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
            title='Zero Delay [um]', value='95.')

        self.stageStartPos = bokeh.models.widgets.TextInput(
                title='Start Position [um]', value='0.01')
                #experiment parameter
        self.sweepTimeInput = bokeh.models.widgets.TextInput(
            title='Integration time [s]', value='10') #seconds
        self.sampleRateInput = bokeh.models.widgets.TextInput(
                title='Sample Rate', value='300')
        self.delay = np.arange(-1000,9000)*(100/10000)*2*3.33564*10**-15
        self.numCycle = 1 # number of cycle after initiation of the wave generator
        self.numSweeps = bokeh.models.widgets.TextInput(
            title='Sweep Number', value='180') # number of sweeps
        self.ppOnlyNum = bokeh.models.widgets.TextInput(
            title='Pump/Probe-Only number', value=str(3600))

        self.averageNum = bokeh.models.widgets.TextInput(
            title='Boxcar Average', value='30') # number of average

        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value='Reflected beam: mW\nTransmitted beam: mW\nFocus size: \nPressure: 5e-7mbar \nSample Rate:300 \nBoxcar averaged: 30\nScan time: \nMCP Voltage: 3800 \nFast Scan', rows=10)

        # arrange items
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.averageNum, self.numSweeps, self.zeroDelInput, self.stageStartPos,
            self.sweepTimeInput, self.sampleRateInput, self.ppOnlyNum,
            self.saveBtn, self.saveNameInput,  self.scanTableBtn, self.comment, width = 200)
        self.layout = bokeh.layouts.grid([
            self.inputs,
            bokeh.layouts.column(
                self.sumAutocorrelationPlot.element, self.sumAutocorrelationPlotD.element, self.linePlot_channel0.element, self.linePlot_channel1.element,
                 self.linePlot_channel2.element, self.linePlot_channel3.element, self.linePlot_channel4.element, self.linePlot_channel5.element,self.linePlot_ref0.element,
                 self.linePlot_ref1.element, self.linePlot_ref2.element, self.linePlot_ref3.element, self.linePlot_ref4.element)
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

    def start(self):
        
        self.ppNum=list(flatten([['pumponly','probeonly'] if i%(int(self.ppOnlyNum.value))==0 else i for i in range(1,int(self.numSweeps.value))]))
        self.totalScanNum = len(self.ppNum)
        print('\n This experiment has ' + str(self.totalScanNum) + ' sweeps.\n')

        #container of the data from daq
        self.sampRate = int(self.sampleRateInput.value)
        self.sweepTime = math.ceil(int(self.sweepTimeInput.value)/1.6)*1.6
        self.sumSpectrum = np.zeros((11, int(self.sampRate * self.sweepTime)))

        #parameters of the digitizer
        self.scanNum = 0
        self.cycles = 3320 #72000 correspongind t0 120.5s of measurement
        self.range = 12032#1536 # 1024 for H2O, 1536 for 2-Proponal
        self.sumSpectrumD = np.zeros(self.cycles)

        #NIDAQmx ceil(t/1.6)
        self.nidaq_reader = PLLreadout_nidaqmx(self.sweepTime, sampRate=self.sampRate, bufferSize=self.sampRate)

        #open shutter
        self.shutter.set_shutter_mode(modes=['F','O'])
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
            self.delayer.setClosedLoop()
            #self.delayer.autoZero()
            #time.sleep(10)
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
                inputs=[[None,None,None,None,None] for i in range(int(self.totalScanNum))],#measurement
                #inputs=[[None,None,None,50] for i in range(int(self.totalScanNum))],#stability test
                sequence=[
                    #measurement.sleep_function(int(0.1)),#stability test
                    measurement.no_input_sequence_function(self.tof_digitizer.start),
                    measurement.sleep_function(5),             
                    measurement.no_input_sequence_function(self.delayer.initWaveGen),#measurement
                    measurement.sleep_function(15),
                    measurement.no_input_sequence_function(self.tof_digitizer.readout_continuous),
                    #measurement.single_input_sequence_function(self.delayer.move_absolute_um),
                    ],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=self.nidaq_reader.start,#here use averageNum replace integration time
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
        im_data = np.transpose(np.reshape(np.array(data[4]), (self.cycles,self.range)))
        while np.sum(self.nidaq_reader.container) == 0:
            time.sleep(0.1)
        curspec = np.reshape(self.nidaq_reader.container,(11, int(self.sampRate * self.sweepTime)))
        self.sumSpectrum = self.sumSpectrum+curspec
        curspecD = np.sum(im_data,0)
        self.sumSpectrumD = self.sumSpectrumD+curspecD
        channel0= curspec[0]
        channel1= curspec[2]
        channel2= curspec[4]
        channel3= curspec[6]
        channel4= curspec[8]
        channel5= curspec[10]
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
            self.linePlot_channel5.update(
                num=0, x=np.arange(channel5.size), y=channel5.flatten())
            self.sumAutocorrelationPlot.update(
                num=0, x=np.arange(channel0.size), y=np.sum(self.sumSpectrum,axis=0).flatten()) #show the sum of channel0 scan
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

            self.sumAutocorrelationPlotD.update(
                num=0, x=np.arange(curspecD.size), y=curspecD) #show the sum of channel0 scan
        except Exception as e:
            print('plot error')
            print(e)

        try:
            # save data hdf5, compress data due to the GB size.
            if self.scanNum == 0:
                self.file.create_dataset('dataB', data=curspec, compression="gzip", chunks=True, maxshape=(None,int(self.sampRate * self.sweepTime)))
                self.file.create_dataset('parameters', data = self.parameters)
                self.file.create_dataset('ppNum', data = str(self.ppNum))
                self.file.create_dataset(
                        'comment', data=self.comment.value,
                        dtype=h5py.special_dtype(vlen=str))
                self.file.flush()

                self.file.create_dataset('dataD', data=im_data, compression="gzip", chunks=True, maxshape=(None,self.cycles))

            else:
                self.file['dataB'].resize((self.file['dataB'].shape[0] + 11), axis=0)
                self.file['dataB'][-11:] = curspec
                self.file['dataD'].resize((self.file['dataD'].shape[0] + im_data.shape[0]), axis=0)
                self.file['dataD'][-im_data.shape[0]:] = im_data
                self.file.flush()

            # save comment to separate txt file
                with open(self.fname + '.txt', 'w') as f:
                    f.write(self.comment.value)
                    
        except Exception as e:
            print('save error!!!')
            print(e)

        if self.ppNum[self.scanNum]=='pumponly':
            try:
                print('\n Now begin to measure pump-only spectra!')
                #self.shutter.set_shutter_mode('U')
            except Exception as e:
                print('shutter error')
                print(e)
        elif self.ppNum[self.scanNum]=='probeonly':
            try:
                print('\n Now begin to measure probe-only spectra!')
                #self.shutter.set_shutter_mode('R')
            except Exception as e:
                print('shutter error')
                print(e)
        else:
            try:
                print('\n This is the No.' + str(self.ppNum[self.scanNum]) + ' sweep.')
                #self.shutter.set_shutter_mode('O')
            except Exception as e:
                print('shutter error')
                print(e)
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
        self.shutter.set_shutter_mode(modes=['K'])
        self.file.close()
    
    def close(self):
        self.shutter.set_shutter_mode(modes=['K'])
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
        if longstage:
            stage = SMC100(1, 'COM21', silent=True)
        else:
            stage = PI_stage('COM23')
        digitizer = mcs6a(cycles=3320, swpreset=10, sweepmode='1e2004')

        # measurement tab
        measurementgui = tof_measurement_gui(
            doc=doc,
            running=self.running,
            tof_digitizer=digitizer,
            delayer=stage)

        #shuttergui = shutter_gui(doc=doc)

        self.title = 'TOF Readout'
        self.tabs = [
            {'layout': measurementgui.layout, 'title': measurementgui.title},
            #{'layout': shuttergui.layout, 'title': shuttergui.title}
            ]

        # this list is auto-closed, all close functions of the
        # added objects are called at session destructioncv 
        self.close_list.append(measurementgui)
        #self.close_list.append(shuttergui)
        self.close_list.append(stage)


print('start tof')
# start the server
bgh.bokeh_gui_helper(tof_session_handler(), 5024)
