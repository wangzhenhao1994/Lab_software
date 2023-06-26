import requests
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import os
import h5py
from functools import partial
import math
import bokeh
from sympy import zeros


from pi_stage import PI_stage
from small_lab_gui.helper import bokeh_gui_helper as bgh
from small_lab_gui.helper import bokeh_plot_helper as bph
from small_lab_gui.helper import measurement
from shutter import Shutter

from tqdm import tqdm

longstage = False

if longstage:
    from smc100pp import SMC100
else:
    from pi_stage import PI_stage

class osc_alignment():
    def __init__(self, doc, running, delayer, osc):
        self.title = 'Alignment'
        # show the total ion count
        self.totalCount = bokeh.models.Div(text='0', width=500, height=500, style={
                                            'font-size': '2000%', 'color': 'blue'})

        # measurement thread
        self.measurement = None
        # bokeh doc for callback
        self.doc = doc
        # hardware
        self.osc = osc
        self.delayer = delayer
        # global measurement running indicator
        self.running = running

        self.startBtn = bokeh.models.widgets.Button(
            label='Start', button_type='success')
        self.stageStartPos = bokeh.models.widgets.TextInput(
                title='Start Position [um]', value='50')        

        # start thread callback
        self.startBtn.on_click(self.start)

        self.layout = bokeh.layouts.grid(
            [bokeh.layouts.row(self.startBtn, self.totalCount, width=800)])

    def start(self):

        # in case this measurement is running, stop it
        if self.running.am_i_running(self):
            self.stop()
        # in case a different measurement is running, do nothing
        elif self.running.is_running():
            pass
        else:
            self.running.now_running(self)
            # switch start to stop button
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'
            # create the measurment thread
            self.measurement = measurement.measurement(
                inputs=None,
                sequence=[
                    measurement.no_input_sequence_function(self.osc.requestData),
                    measurement.sleep_function(1)],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=partial(self.delayer.move_absolute_um,
                            pos=int(self.stageStartPos.value)),
                finish=lambda in1, in2: self.delayer.stop(),
                save_output=False)
        # start the measurment thread
        self.measurement.start()
    
    def update(self, data):
        if not (data is None):
            curspec = data[0]
            self.totalCount.text = str(-np.round(np.sum(curspec)/1000,0))
    
    def stop(self):
        if not (self.measurement is None):
            self.measurement.stop()
            self.measurement.join()
        self.running.now_stopped()
        self.startBtn.label = 'Start'
        self.startBtn.button_type = 'success'
    
    def close(self):
        self.stop()


class oscilloScan():
    def __init__(self, doc, running, delayer, osc):

        self.title = 'Measurement'
        # measurement thread
        self.measurement = None

        self.delayer = delayer
        self.osc = osc

        # global measurement running indicator
        self.running = running
        self.doc = doc

        # pcolor plot to display results
        self.imdata = 0
        self.sumImageSpectrum = 0
        self.sumSpectrum = 0
        self.totalFFT = 0
        self.lastSpectrum = 0
        self.lastFFT = 0
        self.allSpectrum = 0
        self.scanNum = 0


        #add togethor
        self.sumPlot = bph.plot_2d()
        self.sumPlot.line()
        #last scan
        self.linePlot0 = bph.plot_2d()
        self.linePlot0.line(legend='channel0')
        self.linePlot1 = bph.plot_2d()
        self.linePlot1.line(legend='channel1')
        self.linePlot2 = bph.plot_2d()
        self.linePlot2.line(legend='channel2')
        self.linePlot3 = bph.plot_2d()
        self.linePlot3.line(legend='channel3')
        
        #shutter
        self.shutter = Shutter('COM22')

        #buttons and layout
        self.startBtn = bokeh.models.widgets.Button(
            label='Start', button_type='success')
        self.stageStartPos = bokeh.models.widgets.TextInput(
                title='Start Position [um]', value='0.1')        
        #experiment parameter
        self.sweepTimeInput = bokeh.models.widgets.TextInput(
            title='Integration time [s]', value='20') #seconds
        self.delay = np.arange(-1000,9000)*(100/10000)*2*3.33564*10**-15
        self.numCycle = 1 # number of cycle after initiation of the wave generator
        self.numSweeps = bokeh.models.widgets.TextInput(
            title='Sweep Number', value='180') # number of sweeps

        self.comment = bokeh.models.widgets.TextAreaInput(
            title='Comment', value="""Reflected beam:270 mW\nTransmitted beam:250 mW\nFocus size:8.5 \nAverage Of Boxcar: 30 \nPressure:1.3e-6 mBar \nSample: H2 \nMeasured Mass: 1,2,17,18\n""", rows=10)
        self.parameters = None

        self.inputs = bokeh.layouts.Column(
            self.startBtn, self.sweepTimeInput, self.numSweeps, self.stageStartPos, self.comment,
            width = 200
        ) 
        
        self.layout = bokeh.layouts.grid(
            [self.inputs,
            bokeh.layouts.column(
                self.linePlot0.element,self.linePlot1.element,self.linePlot2.element,self.linePlot3.element,
            width=800
            )], ncols=2
            )

        # start thread callback
        self.startBtn.on_click(self.start)

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
            self.running.now_running(self)
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'

            #in future here should be able to set the phase of the wave output of wave generator
            self.delayer.setSweepTime(int(self.sweepTimeInput.value))
            self.delayer.setCycleNum(int(self.numCycle))#number of the cycle after initiate the wave generator
            
            #oscilloscope
            #self.osc.checkDataSource()
            #in the future here should be able to remotely set the parameter of the osciloscope by the IP address.

            # scan start time for save name
            self.now = datetime.datetime.now()

            self.imdata = 0
            self.sumSpectrum = 0
            self.totalFFT = 0
            self.lastSpectrum = 0
            self.lastFFT = 0
            self.allSpectrum = 0
            self.scanNum = 0

            # set integration time
            self.StartPos = float(self.stageStartPos.value)

            # switch start to stop button
            self.startBtn.label = 'Stop'
            self.startBtn.button_type = 'danger'

            # create the measurment thread
            self.measurement = measurement.measurement(
                inputs=[[None,None,self.StartPos,None] for i in range(int(self.numSweeps.value))],
                sequence=[
                    measurement.no_input_sequence_function(self.delayer.initWaveGen),
                    measurement.sleep_function(int(self.sweepTimeInput.value)+2),
                    measurement.single_input_sequence_function(self.delayer.move_absolute_um),
                    measurement.no_input_sequence_function(self.osc.requestData)
                    ],
                update=measurement.bokeh_update_function(
                    self.update, self.doc),
                init=partial(self.delayer.move_absolute_um, pos = self.StartPos),
                finish=measurement.bokeh_no_input_finish_function(
                    self.stop, self.doc),
                save_output=True)
            #log the experiment parameters
            self.parameters ='Experiment Parameters:\n'\
            + 'Sweep time (s):'+ str(self.sweepTimeInput.value) + '\n'\
            +'Start position:' + str(self.stageStartPos.value)  #saved parameters
            # start the measurment thread
            self.measurement.start()

    def update(self, data):
        self.im_data = np.array([d[3] for d in data])
        self.lastSpectrum = self.im_data[-1]
        channel0=self.lastSpectrum[0]
        channel1=self.lastSpectrum[1]
        channel2=self.lastSpectrum[2]
        channel3=self.lastSpectrum[3]

        # update plots
        try:
            self.linePlot0.update(
                num=0, x=self.delay*1e15, y=channel0
            )
            self.linePlot1.update(
                num=0, x=self.delay*1e15, y=channel1
            )
            self.linePlot2.update(
                num=0, x=self.delay*1e15, y=channel2
            )
            self.linePlot3.update(
                num=0, x=self.delay*1e15, y=channel3
            )
        except:
            print("plot error!")

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
                f.create_dataset('data', data=self.im_data)
                f.create_dataset('parameters', data = self.parameters)
                f.create_dataset(
                         'comment', data=self.comment.value,
                         dtype=h5py.special_dtype(vlen=str))
                f.flush()

            # save comment to separate txt file
                with open(fname + '.txt', 'w') as f:
                    f.write(self.comment.value)
        except:
            print('save error')
        self.scanNum += 1
        #print('This is the No.'+str(self.scanNum)+' sweep!')

    def stop(self):
        if not (self.measurement is None):
            self.measurement.stop()
            self.measurement.join()
        self.running.now_stopped()
        self.startBtn.label = 'Start'
        self.startBtn.button_type = 'success'
        self.delayer.stop()
        #self.shutter.set_shutter_mode(modes=['K','P'])
        
    def close(self):
        self.stop()
        #close the shutter after the measurement
        #self.shutter.set_shutter_mode(modes=['K','P'])

class oscScope():
    def __init__(self, dataSource = ['CH1', 'CH2','CH3','CH4'], IP = '129.27.156.200') -> None:
        self.dataSource = dataSource
        self.IP = IP
        self.commandIP = 'http://129.27.156.200/Comm.html'
    
    def checkDataSource(self):
        response = requests.post(
            'http://129.27.156.200/Comm.html', data={'COMMAND': 'DATA:SOURCE?'})
        ds = response.text[634:-93]
        if ds== self.dataSource:
            print('The data source is <' + self.dataSource + '>.')
            pass
        else:
            response = requests.post(
                'http://129.27.156.200/Comm.html', data={'COMMAND': 'DATA:SOURCE '+self.dataSource})
            print('The data source is modified to <' + self.dataSource + '>.')
    
    def requestData(self):
        data=np.zeros((4,10000))
        i=0
        for s in self.dataSource:
            response = requests.post(
                'http://129.27.156.200/Comm.html', data={'COMMAND': 'DATA:SOURCE '+s})
            print('The data source is modified to <' + s + '>.')

            response = requests.post(
                'http://129.27.156.200/Comm.html', data={'COMMAND': 'CURVe?'})
            r = response.text
            endOfHeader = r.find("NAME=\"name\""+">")+len("NAME=\"name\""+">")
            endOfData = r.find("</TEXTAREA>")
            interData = r[endOfHeader:endOfData]  # remove the header info from the response
            data[i] = np.fromstring(interData, sep=',')  # 10k points
            i=i+1
            time.sleep(1)
        return data

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

class osc_session_handler(bgh.bokeh_gui_session_handler):
    def open_session(self, doc):
        self.running = bgh.running()

        if longstage:
            stage = SMC100(1, 'COM21', silent=True)
        else:
            stage = PI_stage('COM23')

        # hardware
        osc = oscScope()
        alignmentgui = osc_alignment(
            doc=doc,
            running=self.running,
            delayer=stage, 
            osc=osc
        )
        measurementgui=oscilloScan(
            doc=doc,
            running=self.running,
            delayer=stage, 
            osc=osc)
        #shuttergui = shutter_gui(doc=doc)

        self.title = 'Oscilloscope Readout'
        self.tabs = [
            {'layout': alignmentgui.layout, 'title': alignmentgui.title},
            {'layout': measurementgui.layout, 'title': measurementgui.title},
            #{'layout': shuttergui.layout, 'title': shuttergui.title}
            ]

        # this list is auto-closed, all close functions of the
        # added objects are called at session destruction
        self.close_list.append(alignmentgui)
        self.close_list.append(measurementgui)
        #self.close_list.append(shuttergui)
        self.close_list.append(stage)
if __name__ == '__main__':
    # start the server
    bgh.bokeh_gui_helper(osc_session_handler(), 5024)
