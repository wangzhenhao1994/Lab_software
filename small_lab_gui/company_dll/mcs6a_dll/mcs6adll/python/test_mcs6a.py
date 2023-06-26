import mcs6a_wrapper

class mcs6a():
	def __init__(self, path = ''):
		self.dll = mcs6a_wrapper.mcs6aDll(path)
		self.nDev = 0

	#def setup(self, integration, roi):

	#def frame(self, integration, roi):

	def help(self):
		print("Commands:")
		print("Q		Quit")
		print("?		Help")
		print("S       Show Status")
		print("H		Halt")
		print("T       Show Setting")
		print("CHN=x   Switch to CHN #x ")
		print("(... more see command language in MPANT help)")
		print("")

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
		if command == "?":
			self.help()
		elif command == "Q":
			return 1
		elif command == "S":
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

mc = mcs6a()
res = mc.dll.GetStatus(0)
res = mc.dll.GetStatusData(0)
mc.PrintMpaStatus(res['Status'])
mc.help()
while True:
	command = input("")
	if mc.run(command):
		break


# lpSet=(IMPAGETSETTING)GetProcAddress(hDLL,"GetSettingData")
# lpNewStat=(IMPANEWSTATUS)GetProcAddress(hDLL,"GetStatus")
# lpStat=(IMPAGETSTATUS)GetProcAddress(hDLL,"GetStatusData")
# lpRun=(IMPARUNCMD)GetProcAddress(hDLL,"RunCmd")
# lpCnt=(IMPAGETCNT)GetProcAddress(hDLL,"LVGetCnt")
# lpRoi=(IMPAGETROI)GetProcAddress(hDLL,"LVGetRoi")
# lpDat=(IMPAGETDAT)GetProcAddress(hDLL,"LVGetDat")
# lpStr=(IMPAGETSTR)GetProcAddress(hDLL,"LVGetStr")
# lpServ=(IMPASERVEXEC)GetProcAddress(hDLL,"ServExec")
# lpGetDatSet=(IMPAGETDATSET)GetProcAddress(hDLL,"GetDatSetting")
# lpGetMCSSet=(IMPAGETMCSSET)GetProcAddress(hDLL,"GetMCSSetting")
# // lpDigInOut=(IMPADIGINOUT)GetProcAddress(hDLL,"DigInOut")
# // lpDacOut=(IMPADACOUT)GetProcAddress(hDLL,"DacOut")
# lpStart=(IMPASTART)GetProcAddress(hDLL,"Start")
# lpHalt=(IMPAHALT)GetProcAddress(hDLL,"Halt")
# lpContinue=(IMPACONTINUE)GetProcAddress(hDLL,"Continue")
# lpErase=(IMPAERASE)GetProcAddress(hDLL,"Erase")
