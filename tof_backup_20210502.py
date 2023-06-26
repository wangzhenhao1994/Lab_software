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



from shutter import Shutter
from calculate_k_b import Calibration_mass
calclator = Calibration_mass(mass=[18,30], pixel=[1028,1455])#def __init__(self, mass=[18.01528,31.99880], pixel=[2659,4575])
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
        # digitizer card
        self.tof_digitizer = tof_digitizer
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
            title='Integration time [ksweeps]', value='3')
        if longstage:
            self.stagePos = bokeh.models.widgets.TextInput(
                title='Stage Position [mm]', value='11.411')
        else:
            self.stagePos = bokeh.models.widgets.TextInput(
                title='Stage Position [um]', value='50.')

        # spectrum plot
        self.linePlot = bph.plot_2d()
        self.linePlot.line(legend='Current')

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
            [self.inputs, self.linePlot.element, self.totalCount],
            ncols=2, nrows=2)

        # start thread callback
        self.startBtn.on_click(self.start)

        #shutter
        #self.shutter = Shutter('COM13')

    def start(self):
        #open shutter
        #self.shutter.set_shutter_mode('F')
        #self.shutter.set_shutter_mode('O')

        #move the stage
        if longstage:
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
                    self.tof_digitizer.readout_continuous,
                    measurement.sleep_function(1)],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=self.tof_digitizer.start_continuous,
                finish=lambda in1, in2: self.tof_digitizer.stop(),
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
            curspec = data[0]['data'][0]
            sweeps = data[0]['starts']
            self.totalCount.text = str(round(np.sum(self.spectrum)))
            if np.abs(curspec - self.lastspectrum).sum():
                self.lastspectrum = curspec
                self.spectrum = curspec-self.subtractspectrum
                self.linePlot.update(
                    num=0, x=self.pixel2mass(np.arange(self.spectrum.size)), y=self.spectrum)
                    #num=0, x=np.arange(self.spectrum.size), y=self.spectrum)
                if sweeps - self.subtractsweeps >= self.integration:
                    self.subtractsweeps = sweeps
                    self.subtractspectrum = curspec
    
    def pixel2mass(self, t, k=k, b=b):
        return ((t-b)/k)**2


class tof_measurement_gui(tof_alignment_gui):
    def __init__(self, doc, running, tof_digitizer, delayer, logbook = None):
        super().__init__(doc, running, tof_digitizer, delayer)
        self.logbook = logbook
        self.title = 'Measurement'

        # pcolor plot to display results
        self.imagePlot = bph.plot_false_color()
        self.imagePlot.image()

        #autocorrelation
        self.autocorrelationPlot = bph.plot_2d()
        self.autocorrelationPlot.line()

        # scan table button
        self.scanTableBtn = bokeh.models.widgets.Toggle(label='Scan Table')
        # measuement inputs
        if longstage:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [mm]', value='11.3503')
        else:
            self.zeroDelInput = bokeh.models.widgets.TextInput(
            title='Zero Delay [um]', value='50.')

        self.startDelInput = bokeh.models.widgets.TextInput(
            title='Start Delay [fs]', value='-5.')
        self.stopDelInput = bokeh.models.widgets.TextInput(
            title='Stop Delay [fs]', value='5.')
        self.stepSizeInput = bokeh.models.widgets.TextInput(
            title='Step Size [fs]', value='0.01')
        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value='Reflected beam: mW\nTransmitted beam: mW\nFocus size: ', rows=10)

        #process input
        self.massMinInput = bokeh.models.widgets.TextInput(
            title='Min Mass', value='5')
        self.massMaxInput = bokeh.models.widgets.TextInput(
            title='Max Mass', value='25')
        self.dcRangeInput = bokeh.models.widgets.TextInput(
            title='DC range', value='2')

        #FFT plot
        self.fftPlot = bph.plot_2d()
        self.fftPlot.x_axis_label='Initial xlabel'
        self.fftPlot.line()

        # arrange items
        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.integrationInput, self.zeroDelInput,
            self.startDelInput, self.stopDelInput, self.stepSizeInput,
            self.saveBtn, self.saveNameInput,  self.scanTableBtn, self.comment)
        self.layout = bokeh.layouts.grid(
            [self.inputs,
            bokeh.layouts.column(
                self.imagePlot.element, bokeh.layouts.row(self.autocorrelationPlot.element),
                self.linePlot.element),
            bokeh.layouts.column(
                self.massMinInput, self.massMaxInput, self.dcRangeInput,
            ),
            bokeh.layouts.column(
                self.fftPlot.element
            )],
            ncols=4)
        self.parameters ='Experiment Parameters:\n'\
            + 'Integration time (ksweeps):'+ str(self.integrationInput.value) + '\n'\
            +'Zero position of stage:' + str(self.zeroDelInput.value) + '\n'\
            +'Start delay:' + str(self.startDelInput.value) + '\n'\
            +'Stop delay:' + str(self.stopDelInput.value) + '\n'\
            +'Step size:' + str(self.stepSizeInput.value)   #saved parameters
        
        #container of real delay
        self.curdelays = []
        self.curdelay = None

    def start(self):

        #open shutter
        #self.shutter.set_shutter_mode(modes=['F','O'])

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
                
                self.delays = np.arange(
                            float(self.startDelInput.value),
                            float(self.stopDelInput.value),
                            float(self.stepSizeInput.value))* 3.0e8 * 1.0e-15 / 2. * 1e6
                self.stage_values = (float(self.zeroDelInput.value)
                                    +self.delays)

            # scan start time for save name
            self.now = datetime.datetime.now()

            # measurement thread
            self.measurement = measurement.measurement(
                inputs=[[pv, None] for pv in self.stage_values],
                sequence=[
                    measurement.single_input_sequence_function(
                        self.delayer.move_absolute_um),#piezo stage
                        #self.delayer.move_absolute_mm),#long stage
                        #self.delayer.abs_move),#for test
                    self.tof_digitizer.frame],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=partial(
                    self.tof_digitizer.setup, integration=self.integration),
                finish=measurement.bokeh_no_input_finish_function(
                    self.stop, self.doc),
                save_output=True)
            self.measurement.start()

    def update(self, data):
        # loop steps
        self.curdelays = self.delays[0:len(data)]
        im_data = np.array([d[1]['data'][0] for d in data])

        #get related pixel range
        pixelMin = calclator.cal_pixel(float(self.massMinInput.value)).astype(int)
        pixelMax = calclator.cal_pixel(float(self.massMaxInput.value)).astype(int)

        #Moniter the stage position
        #print(self.delayer.get_position_mm())

        # get current spectrum
        curspec = im_data[-1]
        im_data = np.transpose(im_data)
        plot_data = im_data[pixelMin:pixelMax]

        # update plots
        try:
            self.linePlot.update(
                num=0, x=self.pixel2mass(np.arange(0, curspec.size)), y=curspec)
            self.imagePlot.update(
                num=0, x=self.curdelays, y=self.pixel2mass(np.arange(pixelMin,pixelMax,1)), z=plot_data)
            self.autocorrelationPlot.update(
                num=0, x=self.curdelays, y=np.sum(plot_data,0))
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
                f.create_dataset('data', data=im_data)
                f.create_dataset('parameters', data = self.parameters)
                f.create_dataset(
                        'comment', data=self.comment.value,
                        dtype=h5py.special_dtype(vlen=str))
                f.flush()

            # save comment to separate txt file
                with open(fname + '.txt', 'w') as f:
                    f.write(self.comment.value)

            # last step, save picture and scan to logbook
            if len(self.curdelays) == len(self.delays):
                plt.clf()
                plt.pcolormesh(im_data)
                # plt.savefig(fname + '.pdf')
                plt.savefig(fname + '.png')
                #if self.logbook:
                #    self.logbook.post(
                #        author='auto-save',
                #        subject='Current Scan: ' + fname + '.hdf5',
                #        text=self.comment.value, filename=fname + '.png')
        except Exception as e:
            print('save error')
            print(e)
    def stop(self):
        super().stop()
        #close the shutter after the measurement
        #self.shutter.set_shutter_mode(modes=['K','P'])



class shutter_gui():
    def __init__(self, doc):
        self.shutter = Shutter('COM22')
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
            stage = SMC100(1, 'COM21', silent=True)
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
        self.close_list.append(digitizer)

if __name__ == '__main__':
    print('start tof')
    # start the server
    bgh.bokeh_gui_helper(tof_session_handler(), 5024)
