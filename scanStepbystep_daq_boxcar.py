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

from small_lab_gui.helper import bokeh_gui_helper as bgh
from small_lab_gui.helper import bokeh_plot_helper as bph
from small_lab_gui.helper import measurement


from nidaqmx_usb6229_fastscan2 import PLLreadout_nidaqmx
from shutter import Shutter
from calculate_k_b import Calibration_mass

from cal_ppNum import flatten

calclator = Calibration_mass(mass=[45,60], pixel=[4649,5363])#def __init__(self, mass=[18.01528,31.99880], pixel=[2659,4575])
[k,b]=calclator.cal_k_b()

longstage = False
testing = False
if not testing:
    # for the lab
    from small_lab_gui.digitizers.digitizer_fast_mcs6a import mcs6a
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


class tof_alignment_gui():
    def __init__(self, doc, running, tof_digitizer, delayer):
        self.title = 'Alignment'
        self.spectrum_length = tof_digitizer.range
        self.spectrum = []

        # measurement thread
        self.measurement = None
        # bokeh doc for callback
        self.doc = doc

        # global measurement running indicator
        self.running = running
        # delay stage
        self.delayer = delayer

        # for continuous mode
        self.subtractsweeps = 0
        self.subtractstarts = 0
        self.subtractruntime = 0
        self.subtractspectrum = 0
        self.lastspectrum = 0

        # Set up widgets
        self.startBtn = bokeh.models.widgets.Button(
            label='Start', button_type='success')
        self.integrationInput = bokeh.models.widgets.TextInput(
            title='Integration time [s]', value='1')
        if longstage:
            self.stagePos = bokeh.models.widgets.TextInput(
                title='Stage Position [mm]', value='-102.5065')
        else:
            self.stagePos = bokeh.models.widgets.TextInput(
                title='Stage Position [um]', value='50.')

        # spectrum plot
        self.sumAutocorrelationPlot = bph.plot_2d()
        self.sumAutocorrelationPlot.line(legend='SumAllMass')

        # show the total ion count
        self.totalCount = bokeh.models.Div(text='0', width=500, height=500, style={'font-size': '2000%', 'color': 'blue'})

        # save button
        self.saveBtn = bokeh.models.widgets.Button(
            label='Save Spectrum', button_type='success')
        self.saveBtn.on_click(self.save_spectrum)
        self.saveNameInput = bokeh.models.widgets.TextInput(
            title='Legend Name', value='Name')

        # arrange layout
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.integrationInput, self.saveBtn,
            self.saveNameInput, self.stagePos)
        self.layout = bokeh.layouts.grid(
            [self.inputs, self.sumAutocorrelationPlot.element, self.totalCount],
            ncols=2, nrows=2)

        # start thread callback
        self.startBtn.on_click(self.start)

        #shutter
        self.shutter = Shutter('COM13')

    def start(self):
        #open shutter
        self.shutter.set_shutter_mode('F')
        #self.shutter.set_shutter_mode('O')

        #!!!!put the photon counter here later

        #move the stage
        if longstage:
            self.delayer.set_speed_mm(20)
            self.delayer.move_absolute_mm(float(self.stagePos.value))
        else:
            self.delayer.move_absolute_um(float(self.stagePos.value))

        # in case this measurement is running, stop it
        if self.running.am_i_running(self):
            self.stop()
        # in case a different measurement is running, do nothing
        elif self.running.is_running():
            pass
        else:
            # set running indicator to block double readout
            self.running.now_running(self)
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'
            # initialize data array
            self.spectrum = 0

            self.subtractsweeps = 0
            self.subtractstarts = 0
            self.subtractruntime = 0
            self.subtractspectrum = 0
            self.lastspectrum = 0



            # set integration time
            self.integration = float(self.integrationInput.value)*1000.

            # create the measurment thread
            self.measurement = measurement.measurement(
                inputs=None,
                sequence=[
                    self.nidaq_reader.readout_continuous,
                    measurement.sleep_function(1)],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=self.nidaq_reader.start_continuous,
                finish=lambda in1, in2: self.nidaq_reader.stop(),
                save_output=False)
            # start the measurment thread
            self.measurement.start()

    def save_spectrum(self):
        self.linePlot.save_current(name=self.saveNameInput.value, num=0)

    def stop(self):
        if not (self.measurement is None):
            self.measurement.stop()
            self.measurement.join()
        self.running.now_stopped()
        self.startBtn.label = 'Start'
        self.startBtn.button_type = 'success'

    def close(self):
        self.stop()

    def update(self, data):
        if not (data is None):
            spec = data[0]['data'][0]
            sweeps = data[0]['starts']
            self.totalCount.text = str(round(np.sum(self.spectrum)))
            if np.abs(spec - self.lastspectrum).sum():
                self.lastspectrum = spec
                self.spectrum = spec-self.subtractspectrum
                self.linePlot.update(
                    num=0, x=self.pixel2mass(np.arange(self.spectrum.size)), y=self.spectrum)
                    #num=0, x=np.arange(self.spectrum.size), y=self.spectrum)
                if sweeps - self.subtractsweeps >= self.integration:
                    self.subtractsweeps = sweeps
                    self.subtractspectrum = spec
    
    def pixel2mass(self, t, k=k, b=b):
        return ((t-b)/k)**2


class tof_measurement_gui(tof_alignment_gui):
    def __init__(self, doc, running, tof_digitizer, delayer, logbook = None):
        super().__init__(doc, running, tof_digitizer, delayer)
        self.logbook = logbook
        self.title = 'Measurement'

        # scan table button
        self.scanTableBtn = bokeh.models.widgets.Toggle(label='Scan Table')

        self.startDelInput = bokeh.models.widgets.TextInput(
            title='Start Delay [fs]', value='-500.')
        self.stopDelInput = bokeh.models.widgets.TextInput(
            title='Stop Delay [fs]', value='50000.')
        self.stepSizeInput = bokeh.models.widgets.TextInput(
            title='Step Size [fs]', value='7.0')
        self.ppOnlyNum = bokeh.models.widgets.TextInput(
            title='Pump/Probe-Only number', value=str(10000000000000000000))
        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value='Reflected beam: mW\nTransmitted beam: mW\nFocus size: \nIntegrated time every step: \nSample Rate:30\nMCP Voltage: ', rows=10)

        # measuement inputs
        if longstage:
            self.delayer.set_speed_mm(20)
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [mm]', value='-102.5065')
        else:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [um]', value='7.')

        

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

        # arrange items
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.integrationInput, self.zeroDelInput,
            self.startDelInput, self.stopDelInput, self.stepSizeInput,self.ppOnlyNum,
            self.saveBtn, self.saveNameInput,  self.scanTableBtn, self.comment)
        self.layout = bokeh.layouts.grid(
            [self.inputs,
            bokeh.layouts.column(
                self.sumAutocorrelationPlot.element, self.linePlot_channel0.element, self.linePlot_channel1.element,
                 self.linePlot_channel2.element, self.linePlot_channel3.element, self.linePlot_channel4.element,self.linePlot_ref0.element,
                 self.linePlot_ref1.element, self.linePlot_ref2.element, self.linePlot_ref3.element, self.linePlot_ref4.element)],
            ncols=4)

        
        #container of real delay
        self.curdelays = []
        self.curdelay = None

        #parameters of the scan
        self.scanNum = 0

    def start(self):

        #NIDAQmx
        #container of the data from daq
        self.sampRate = 30
        self.nidaq_reader = PLLreadout_nidaqmx(float(self.integrationInput.value), sampRate=self.sampRate, bufferSize=self.sampRate, triggerSrc="/Dev1/PFI1")
        
        #open shutter
        self.shutter.set_shutter_mode('F')

        # in case this measurement is running, stop it
        if self.running.am_i_running(self):
            self.stop()
        # in case a different measurement is running, do nothing
        elif self.running.is_running():
            pass
        else:
            # set running indicator to block double readout
            self.running.now_running(self)
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'
            # integration time
            self.integration = float(self.integrationInput.value)*1000
            # delay vector setup
            if self.scanTableBtn.active:
                self.delays = np.loadtxt('scantable.txt')
            else:
                if longstage:
                    #fs to um, considering into the factor 2 and set the delay intergal times of 0.5 um.
                    fs2mm = lambda a: math.floor(a* 3.0e8 * 1.0e-15 / 2. * 1e3 *20000)/20000
                    startDelInput = fs2mm(float(self.startDelInput.value))
                    stopDelInput = fs2mm(float(self.stopDelInput.value))
                    stepSizeInput = fs2mm(float(self.stepSizeInput.value))
                    print('The step size is '+ str(stepSizeInput)+' mm\n')
                    self.delays = np.arange(startDelInput,stopDelInput,stepSizeInput)
                else:
                    self.delays = np.arange(
                                float(self.startDelInput.value),
                                float(self.stopDelInput.value),
                                float(self.stepSizeInput.value))* 3.0e8 * 1.0e-15 / 2. * 1e6
                self.stage_values = (float(self.zeroDelInput.value)
                                    +self.delays)
                print(self.stage_values[0:3])
            stepNum = self.delays.size
            self.scanNum = 0

            # scan start time for save name
            self.now = datetime.datetime.now()

            self.parameters ='Experiment Parameters:\n'\
            + 'Integration time (ksweeps):'+ str(self.integrationInput.value) + '\n'\
            +'Zero position of stage:' + str(self.zeroDelInput.value) + '\n'\
            +'Start delay:' + str(self.startDelInput.value) + '\n'\
            +'Stop delay:' + str(self.stopDelInput.value) + '\n'\
            +'Step size:' + str(self.stepSizeInput.value)   #saved parameters
            # measurement thread
            print(self.stage_values)
            self.measurement = measurement.measurement(
                inputs=[[pos, None, None] for pos in self.stage_values],
                sequence=[
                    measurement.single_input_sequence_function(
                        self.delayer.move_absolute_um),#piezo stage
                        #self.delayer.move_absolute_mm),#long stage
                        #self.delayer.abs_move),#for test
                    measurement.sleep_function(int(0.5)),
                    measurement.no_input_sequence_function(self.nidaq_reader.read)],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=None,
                finish=measurement.bokeh_no_input_finish_function(
                    self.stop, self.doc),
                save_output=True)
            self.measurement.start()

    def update(self, data):
        # loop steps
        self.curdelays = self.delays[0:len(data)]
        spec = np.array([d[2] for d in data])
        sumSpec = np.sum(spec,axis=1) # sum the count of all the mass

        channel0= spec[:,0]
        channel1= spec[:,2]
        channel2= spec[:,4]
        channel3= spec[:,6]
        channel4= spec[:,8]
        ref0= spec[:,1]
        ref1= spec[:,3]
        ref2= spec[:,5]
        ref3= spec[:,7]
        ref4= spec[:,9]

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
                num=0, x=np.arange(channel0.size), y=sumSpec) #show the sum of channel0 scan
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

        # save scan every step
        try:
            os.makedirs(
                self.now.strftime('%Y-%m') + '/'
                + self.now.strftime('%Y-%m-%d'), exist_ok=True)
            fname = (self.now.strftime('%Y-%m') + '/'
                     + self.now.strftime('%Y-%m-%d')
                     + '/scan_tof_'
                     + self.now.strftime('%Y-%m-%d-%H-%M-%S'))
            # save data hdf5
            with h5py.File(fname + '.hdf5', 'w') as f:
                f.create_dataset('delays', data=self.curdelays)
                f.create_dataset('stagePos', data=self.stage_values)
                f.create_dataset('data', data=spec)
                f.create_dataset('parameters', data = self.parameters)
                f.create_dataset(
                        'comment', data=self.comment.value,
                        dtype=h5py.special_dtype(vlen=str))
                f.flush()

            # save comment to separate txt file
                with open(fname + '.txt', 'w') as f:
                    f.write(self.comment.value)

        except Exception as e:
            print('save error')
            print(e)

        self.scanNum += 1
    def stop(self):
        super().stop()
        #close the shutter after the measurement
        #self.shutter.set_shutter_mode(modes=['K'])



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
        digitizer = mcs6a()

        if longstage:
            stage = SMC100(1, 'COM7', silent=True)
        else:
            stage = PI_stage('COM23')

        # open logbook to auto-save scans
        # logbook = elog(host='localhost', port=8080, logbook='demo')

        # alignment tab
        alignmentgui = tof_alignment_gui(
            doc=doc,
            running=self.running,
            tof_digitizer=digitizer,
            delayer=stage)

        # measurement tab
        measurementgui = tof_measurement_gui(
            doc=doc,
            running=self.running,
            tof_digitizer=digitizer,
            delayer=stage)

        shuttergui = shutter_gui(doc=doc)

        self.title = 'TOF Readout'
        self.tabs = [
            {'layout': alignmentgui.layout, 'title': alignmentgui.title},
            {'layout': measurementgui.layout, 'title': measurementgui.title},
            {'layout': shuttergui.layout, 'title': shuttergui.title}]

        # this list is auto-closed, all close functions of the
        # added objects are called at session destruction
        self.close_list.append(alignmentgui)
        self.close_list.append(measurementgui)
        self.close_list.append(shuttergui)
        self.close_list.append(stage)

if __name__ == '__main__':
    print('start tof')
    # start the server
    bgh.bokeh_gui_helper(tof_session_handler(), 5024)
