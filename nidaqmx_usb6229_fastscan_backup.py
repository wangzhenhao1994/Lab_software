import time
import numpy as np
import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from matplotlib import pyplot as plt
system = nidaqmx.system.System.local()
system.driver_version

for device in system.devices:
    print(device.name)

class PLLreadout_nidaqmx(object):
    def __init__(self) -> None:
        super().__init__()
        self.Ch00_name = 'A00'
        self.fs_acq = 1000 #sample frequency

    def sleep(self, duration, get_now=time.perf_counter):
        now = get_now()
        end = now + duration
        while now < end:
            now = get_now()

    def read(self):
        delay_monitor = []
        with nidaqmx.Task() as task, nidaqmx.Task() as task2, nidaqmx.Task() as task3:
            task.ai_channels.add_ai_voltage_chan(physical_channel="dev1/ai0", name_to_assign_to_channel=self.Ch00_name)
            task2.di_channels.add_di_chan(lines="Dev1/PFI0")#PFI0 is the trigger from the Standform delayer generator
            #task3.di_channels.add_di_chan(lines="Dev1/PFI4")#PFI4 is the stop trigger (SYNC 1) from the digitizer
            task.timing.cfg_samp_clk_timing(rate=self.fs_acq, sample_mode=constants.AcquisitionType.CONTINUOUS) # you may not need samps_per_chan     
            # input_buf_size
            samples_per_buffer = int(self.fs_acq // 100)  # update frequency 10
            # task.in_stream.input_buf_size = samples_per_buffer * 10  # plus some extra space      
            reader = stream_readers.AnalogMultiChannelReader(task.in_stream)     
            def reading_task_callback(task_idx, event_type, num_samples, callback_data):
                """After data has been read into the NI buffer this callback is called to read in the data from the buffer.     
                This callback is for working with the task callback register_every_n_samples_acquired_into_buffer_event.        
                Args:
                    task_idx (int): Task handle index value
                    event_type (nidaqmx.constants.EveryNSamplesEventType): ACQUIRED_INTO_BUFFER
                    num_samples (int): Number of samples that was read into the buffer.
                """
                buffer = np.zeros((1,num_samples), dtype=np.float64)
                reader.read_many_sample(buffer, num_samples, timeout=constants.WAIT_INFINITELY)     
                # Convert the data from channel as a row order to channel as a column
                data = buffer.T.astype(np.float64)
                try:
                    delay_monitor.append(data)
                    return 0
                except Exception as e:
                    print(e)
                    return 1


            task.register_every_n_samples_acquired_into_buffer_event(samples_per_buffer, reading_task_callback)

            while task2.read(1)[0] is False:
                self.sleep(0.0005)
                #print(0)
            task.start()
            while task2.read(1)[0] is True:
                self.sleep(0.0005)
                #print(1)
            #time.sleep(10)
            #task.stop()
        return delay_monitor
            
if __name__ == '__main__':
    a = PLLreadout_nidaqmx()
    
    delay =a.read()
    delay = np.array(delay).flatten()
    print(delay)


    plt.plot(delay)
    plt.show()


