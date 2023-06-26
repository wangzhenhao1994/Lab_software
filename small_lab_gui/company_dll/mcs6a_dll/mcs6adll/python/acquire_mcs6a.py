#acquire_mcs6a.py
import mcs6a_wrapper
import time
import numpy

from ctypes import *


class mcs6a():
	def __init__(self, path = ''):
		self.dll = mcs6a_wrapper.mcs6aDll(path)
		self.nDev = 0

	def PrintMpaStatus(self, Stat):
		if Stat.started == 1:
			print("ON")
		elif Stat.started == 3: 
			print("READ OUT")
		else:
			print("OFF")
		print("runtime=  {:f}".format(Stat.cnt[self.dll.ST_RUNTIME]))
		print("sweeps=   {:f}".format(Stat.cnt[self.dll.ST_SWEEPS]))
		print("starts=   {:f}".format(Stat.cnt[self.dll.ST_STARTS]))

	def PrintStatus(self, Stat):
		print("totalsum= {:f}".format(Stat.cnt[self.dll.ST_TOTALSUM]))
		print("roisum=   {:f}".format(Stat.cnt[self.dll.ST_ROISUM]))
		print("rate=     {:f}".format(Stat.cnt[self.dll.ST_ROIRATE]))
		print("ofls=     {:f}".format(Stat.cnt[self.dll.ST_OFLS]))

	def PrintDatSetting(self, Set):
		print("savedata= {:d}".format(Set.savedata))
		print("autoinc=  {:d}".format(Set.autoinc))
		print("fmt=      {:d}".format(Set.fmt))
		print("mpafmt=   {:d}".format(Set.mpafmt))
		print("sephead=  {:d}".format(Set.sephead))
		print("filename= {:s}".format(Set.filename.decode("utf-8")))

	def PrintMCSSetting(self, Set):
		print("sweepmode=  0x{:x}".format(Set.sweepmode))
		print("prena=      0x{:x}".format(Set.prena))
		print("cycles=     {:d}".format(Set.cycles))
		print("sequences=  {:d}".format(Set.sequences))
		print("syncout=    0x{:x}".format(Set.syncout))
		print("digio=      0x{:x}".format(Set.digio))
		print("digval=     {:d}".format(Set.digval))
		print("dac0=       0x{:x}".format(Set.dac0))
		print("dac1=       0x{:x}".format(Set.dac1))
		print("dac2=       0x{:x}".format(Set.dac2))
		print("dac3=       0x{:x}".format(Set.dac3))
		print("dac4=       0x{:x}".format(Set.dac4))
		print("dac5=       0x{:x}".format(Set.dac5))
		print("fdac=       0x{:x}".format(Set.fdac))
		print("tagbits=    {:d}".format(Set.tagbits))
		print("extclk=     {:d}".format(Set.extclk))
		print("maxchan=    {:d}".format(Set.maxchan))
		print("serno=      {:d}".format(Set.serno))
		print("ddruse=     0x{:x}".format(Set.ddruse))
		print("active=     {:d}".format(Set.active))
		print("holdafter=  {:g}".format(Set.holdafter))
		print("swpreset=   {:g}".format(Set.swpreset))
		print("fstchan=    {:g}".format(Set.fstchan))
		print("timepreset= {:g}".format(Set.timepreset))

	def PrintSetting(self, Set):
		print("range=     {:d}".format(Set.range))
		print("cftfak=    0x{:x}".format(Set.cftfak))
		print("roimin=    {:d}".format(Set.roimin))
		print("roimax=    {:d}".format(Set.roimax))
		print("nregions=  {:d}".format(Set.nregions))
		print("caluse=    {:d}".format(Set.caluse))
		print("calpoints= {:d}".format(Set.calpoints))
		print("param=     0x{:x}".format(Set.param))
		print("offset=    0x{:x}".format(Set.offset))
		print("xdim=      {:d}".format(Set.xdim))
		print("bitshift=  {:d}".format(Set.bitshift))
		print("active=    0x{:x}".format(Set.active))
		print("roipreset= {:g}".format(Set.eventpreset))

	def run(self, command):
		if command == "S":
			res = self.dll.GetStatusData(self.nDev)
			if self.nDev:
				self.PrintStatus(res['Status'])
			else:
				self.PrintMpaStatus(res['Status'])
		elif command == "T":
			#spectra settings
			res = self.dll.GetSettingData(self.nDev)
			print("CHN {:d}:".format(self.nDev))
			self.PrintSetting(res['Setting'])
			
			if self.nDev==0:#        // MPA settings
				res = self.dll.GetMCSSetting(0)
				self.PrintMCSSetting(res['Board'])
				res = self.dll.GetDatSetting()
				self.PrintDatSetting(res['Defdat'])

		elif command == "H":
			self.dll.Halt(0)
		elif command[0:4] == "CHN=":
			self.nDev = int(command[4])
			self.dll.RunCmd(0, command)
		elif command == "MPA":
			self.nDev=0
			self.dll.RunCmd(0, command)
		else:
			self.dll.RunCmd(0, command)
			print("{:s}".format(command))

#init dll
#print('opening dll')
mc = mcs6a()
#print('status: ' + str(mc.dll.GetStatus(0)))
#status such as last sweeps count and scan length
#res = mc.dll.GetStatusData(0)
#mc.PrintMpaStatus(res['Status'])

# LSB first
# 0x0 = 0000 is for normal mode
# 0x8 = 0001 for start event generation
# 0x2 = 0100 is tag bits off and start with rising edge
# 0x8 = 0001 is enable start events that go to channel 4
# 0x0 = 0000 is enable all channels
# 0x0 = 0000 is enable all channels
# 0x00 not important
mc.dll.RunCmd(0, 'sweepmode=00000280')
# 0x10 = 00001000 is to enable start preset, sweep preset is 0x04 = 00100000, 0x1 is real time preset
mc.dll.RunCmd(0, 'prena=10')
mc.dll.RunCmd(0, 'range=8192')
# mc.dll.RunCmd(0, 'roimin=1')
# mc.dll.RunCmd(0, 'roimax=8192')
mc.dll.RunCmd(0, 'swpreset=12000')
mc.dll.RunCmd(0, 'rtpreset=2')


for cnt2 in range(5):
	start_time = time.time()

	#start acquisition
	mc.dll.Start(0)
	#wait until acq starts
	while not mc.dll.GetStatusData(0)['Status'].started:
		time.sleep(0.01)
	#wait until acq finishes
	while mc.dll.GetStatusData(0)['Status'].started:
		time.sleep(0.01)
	#status such as last sweeps count and scan length
	mc.PrintMpaStatus(mc.dll.GetStatusData(0)['Status'])
	data = mc.dll.LVGetDat(0)['data']
	print(data.sum())

	print("--- %s seconds ---" % (time.time() - start_time))


