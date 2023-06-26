from seabreeze.spectrometers import list_devices, Spectrometer
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

class Spec(object):
    # a wrapper for the spectrometer

    def __init__(self, doc, running, spec):
        # measurement thread
        self.measurement = None
        # bokeh doc for callback
        self.doc = doc
        # global measurement running indicator
        self.running = running

        self.title = 'Spectrometer'

        self.spec = spec
        self.wavelength = self.spec.wavelengths()
        self.shape = self.wavelength.shape[0]

        #input parameter
        self.integrationInput = bokeh.models.widgets.TextInput(
            title='Integration time [ms]', value='100')
        self.averageNum = bokeh.models.widgets.TextInput(
            title='Averaged number', value='1') # number of average

        self.startBtn = bokeh.models.widgets.Button(
            label='start', button_type='success')
        self.startBtn.on_click(self.start)
        self.saveBtn = bokeh.models.widgets.Button(
            label='Save Spectrum', button_type='success')
        self.saveBtn.on_click(self.saveSpectra)
        self.saveNameInput = bokeh.models.widgets.TextInput(
            title='Legend Name', value='Name')

        #plot
        #f=h5py.File(r'C:\Users\TU-IEP-Schultze\Documents\Experiment\femto_ion_spectra\2022-06\2022-06-05\spec.hdf5', 'r')
        #spec2comp = np.array(f['spec_2022-06-05-12-58-14'])
        f=h5py.File(r'C:\Users\TU-IEP-Schultze\Documents\Experiment\femto_ion_spectra\2022-09\2022-09-12\spec.hdf5', 'r')
        spec2comp = np.array(f['spec_2022-09-12-13-31-19'])
        f.close()
        self.linePlot = bph.plot_2d(height=512,width=900)
        self.linePlot.line()
        self.linePlot.plot.line(x=self.wavelength,y=spec2comp,level='underlay')

        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.integrationInput, self.averageNum, self.saveBtn, self.saveNameInput,width=150)
        self.layout = bokeh.layouts.grid([self.inputs,self.linePlot.element],ncols=2)

    def updateSpectra(self):
        spec=[0] * self.shape
        for i in range(int(self.averageNum.value)):
            self.spec.integration_time_micros(int(self.integrationInput.value)*1000)
            spec=spec+self.spec.intensities()
        spec=np.array(spec,dtype='float64')
        return spec

    def start(self):
        # in case this measurement is running, stop it
        if self.running.am_i_running(self):
            self.stop()
        # in case a different measurement is running, do nothing
        elif self.running.is_running():
            pass
        else:
            # set running indicator to block double readout
            self.running.now_running(self)
            # switch start to stop button
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'
            self.measurement = measurement.measurement(
                    inputs=None,
                    sequence=[
                        measurement.no_input_sequence_function(self.updateSpectra)
                        ],
                    update=measurement.bokeh_update_function(
                        self.update, self.doc),
                    init=None,#here use averageNum replace integration time
                    finish=measurement.bokeh_no_input_finish_function(
                        self.stop, self.doc),
                    save_output=False)
            self.measurement.start()
    
    def update(self,data):
        spec=data[0]
        # update plots
        try:
            self.linePlot.update(
                num=0, x=self.wavelength, y=spec)
        except Exception as e:
            print('plot error')
            print(e)

    def saveSpectra(self):
        self.stop()
        self.linePlot.save_current(name=self.saveNameInput.value, num=0)
        self.now = datetime.datetime.now()
        try:
            os.makedirs(
                self.now.strftime('%Y-%m') + '/'
                + self.now.strftime('%Y-%m-%d'), exist_ok=True)
            filename = (self.now.strftime('%Y-%m') + '/'
                    + self.now.strftime('%Y-%m-%d')
                    + '/spec')
            specname ='spec_' + self.now.strftime('%Y-%m-%d-%H-%M-%S')
            
            with h5py.File(filename + '.hdf5', 'a')as f:
                f.create_dataset(specname, data = self.updateSpectra())
                f.create_dataset('wavelength',data=self.wavelength)
        except Exception as e:
            print('save error')
            print(e)
    
    def stop(self):
        if not (self.measurement is None):
            self.measurement.stop()
            self.measurement.join()
        self.running.now_stopped()
        self.startBtn.label = 'Start'
        self.startBtn.button_type = 'success'
    
    def close(self):
        super().stop()
    
class spec_session_handler(bgh.bokeh_gui_session_handler):
    def open_session(self, doc):
        self.running = bgh.running()
        spectrometer = Spectrometer.from_first_available()
        specgui = Spec(doc=doc,
            running=self.running,
            spec=spectrometer)
        self.title = 'Spectrometer'
        self.tabs = [
            {'layout': specgui.layout, 'title': specgui.title}]
        self.close_list.append(Spec)

# start the server
bgh.bokeh_gui_helper(spec_session_handler(), 5020)