from ctypes import *
from ctypes import wintypes
import os
import numpy

class mcs6aDll():
	def __init__(self, path=''):
		if path:
			os.chdir(path)
		self.dll = cdll.LoadLibrary('DMCS6.dll')

	def __del__(self):
		pass

	class COMCTL(Structure):
		_fields_ = [
			('use', c_int),
			('port', c_int),
			('baud', c_ulong),
			('dbits', c_int),
			('sbits', c_int),
			('parity', c_int),
			('echo', c_int),
			('hwndserver', wintypes.HWND),
			('cmd', wintypes.LPSTR)
		]

	ST_RUNTIME = 0
	ST_OFLS = 1
	ST_TOTALSUM = 2
	ST_ROISUM = 3
	ST_ROIRATE = 4
	ST_SWEEPS = 5
	ST_STARTS = 6

	class ACQSTATUS(Structure):
		_fields_ = [
			('started', c_ulong),
			('maxval', c_ulong),
			('cnt', c_double*8)
		]

	class DATSETTING(Structure):
		_fields_ = [
			('savedata', c_long),#bit 0: auto save after stop #bit 1: write listfile #bit 2: listfile only, no evaluation
			('autoinc', c_long),#1 if auto increment filename
			('fmt', c_long),# format type (seperate spectra): # 0 == ASCII, 1 == binary,# 2 == CSV
			('mpafmt', c_long),# format used in mpa datafiles 
			('sephead', c_long),# seperate Header 
			('smpts', c_long),
			('caluse', c_long),
			('filename', c_char*256),
			('specfile', c_char*256),
			('command', c_char*256)
		]


	class REPLAYSETTING(Structure):
		_fields_ = [
			('use', c_long),# 1 if Replay Mode ON
			('modified', c_long),# Bit 0: 1 if different settings are used # (Bit 1: Write ASCII, reserved)
			('limit', c_long),# 0: all, # 1: limited sweep range
			('speed', c_long),# replay speed in units of 100 kB / sec
			('startsfrom', c_double),# first start#
			('startsto', c_double),# last start#
			('startspreset', c_double),# last start - first start
			('filename', c_char*256)
		]

	class ACQSETTING(Structure):
		_fields_ = [
			('range', c_long),# spectrum length
			('cftfak', c_long),# LOWORD: 256 * cft factor (t_after_peak / t_to_peak) # HIWORD: max pulse width for CFT 
			('roimin', c_long),# lower ROI limit
			('roimax', c_long),# upper limit: roimin <= channel < roimax
			('nregions', c_long),# number of regions
			('caluse', c_long),# bit0: 1 if calibration used, higher bits: formula
			('calpoints', c_long),# number of calibration points
			('param', c_long),# (reserved:) for MAP and POS: LOWORD=x, HIWORD=y 
			('offset', c_long),# (reserved:) zoomed MAPS: LOWORD: xoffset, HIWORD, yoffset
			('xdim', c_long),#(reserved:) x resolution of maps
			('bitshift', c_ulong),# LOWORD: Binwidth = 2 ^ (bitshift) # HIWORD: Threshold for Coinc
			('active', c_long),# LOWORD: Binwidth = 2 ^ (bitshift) # HIWORD: Threshold for Coinc
								# Spectrum definition words for CHN1..6:
												# active & 0xF  ==0 not used 
												#               ==1 single
												# bit 8: Enable Tag bits
												# bit 9: start with rising edge 
												# bit 10: time under threshold for pulse width
												# bit 11: pulse width mode for any spectra with both edges enabled
												# Spectrum definition words for calc. spectra:
												# active & 0xF  ==3 MAP, ((x-xoffs)>>xsh) x ((y-yoffs)>>ysh)
												#                 ((x-xoffs)>>xsh) x ((y-timeoffs)>>timesh)  
												#              or ((x-timeoffs)>>timesh x ((y-yoffs)>>ysh)  
												#         bit4=1: x zoomed MAP
												#         bit5=1: y zoomed MAP
												#               ==5 SUM, (x + y)>>xsh
												#               ==6 DIFF,(x - y + range)>>xsh
												#               ==7 ANY, (for compare)
												#               ==8 COPY, x
												#               ==9 DLL  fDLL(x,y,z), 
												#               ==0xA Sweep HISTORY, Sweepnum(x)
												# bit 8..11 xsh, bit 12..15 ysh or bit 8..15 xsh
												# HIWORD(active) = condition no. (0=no condition)
			('eventpreset', c_double),# ROI preset value
			('dummy1', c_double),# (for future use..)
			('dummy2', c_double),
			('dummy3', c_double)
		]

	class EXTACQSETTING(Structure):
		_fields_ = [
			('range', c_long),            # spectrum length
			('cftfak', c_long),           # LOWORD: 256 * cft factor (t_after_peak / t_to_peak)
									# HIWORD: max pulse width for CFT 
			('roimin', c_long),           # lower ROI limit
			('roimax', c_long),           # upper limit: roimin <= channel < roimax
			('nregions', c_long),         # number of regions
			('caluse', c_long),           # bit0: 1 if calibration used, higher bits: formula
			('calpoints', c_long),        # number of calibration points
			('param', c_long),            # (reserved:) for MAP and POS: LOWORD=x, HIWORD=y 
			('offset', c_long),           # (reserved:) zoomed MAPS: LOWORD: xoffset, HIWORD, yoffset
			('xdim', c_long),			#  (reserved:) x resolution of maps
			('bitshift', c_ulong),  # LOWORD: Binwidth = 2 ^ (bitshift)
									# HIWORD: Threshold for Coinc
			('active', c_long),      # Spectrum definition words for CHN1..6:
									# active & 0xF  ==0 not used 
									#               ==1 enabled
								# bit 8: Enable Tag bits
								# bit 9: start with rising edge 
								# bit 10: time under threshold for pulse width
								# bit 11: pulse width mode for any spectra with both edges enabled
							# Spectrum definition words for calc. spectra:
									# active & 0xF  ==3 MAP, ((x-xoffs)>>xsh) x ((y-yoffs)>>ysh)
									#         bit4=1: x zoomed MAP
									#         bit5=1: y zoomed MAP
									#               ==5 SUM, (x + y)>>xsh
									#               ==6 DIFF,(x - y + range)>>xsh
									#               ==7 ANY, (for compare)
									#               ==8 COPY, x
									#               ==10 SW-HIS, Sweep History 
									# bit 8..11 xsh, bit 12..15 ysh or bit 8..15 xsh
									# HIWORD(active) = condition no. (0=no condition)
			('eventpreset', c_double),   # ROI preset value
			('dummy1', c_double),        # (for future use..)
			('dummy2', c_double),		# 
			('dummy3', c_double),        # 
								# MPANT or Server private saved settings:
			('type', c_long),			# 0=single, 1=MAP, 2=ISO...
			('ydim', c_long),		# y resolution of maps
			('reserved', c_long*16)
		]

	class BOARDSETTING(Structure):
		_fields_ = [
			('sweepmode', c_long),       # sweepmode & 0xF: 0 = normal, 
								# 1=differential (relative to first stop in sweep)
								# 4=sequential
								# 5=seq.+diff (Ch1), bit0 = differential mode
								# 6 = CORRELATIONS
								# 7 = diff.+Corr.
								# 9=differential to stop in Ch2, bit3 = Ch2 ref (diff.mode)
								# 0xD = seq.+diff (Ch2)
								# 0xF = Corr.+diff (Ch2)
								# bit 4: Softw. Start
								# bit 6: Endless
								# bit 7: Start event generation
								# bit 8: Enable Tag bits
								# bit 9: start with rising edge 
								# bit 10: time under threshold for pulse width
								# bit 11: pulse width mode for any spectra with both edges enabled
								# bit 12: abandon Sweepcounter in Data
								# bit 13: "one-hot" mode with tagbits
								# bit 14: ch6 ref (diff.mode)
								# bit 15: enable ch6 input
								# bit 16..bit 20 ~(input channel enable) 
								# bit 24: require data lost bit in data
								# bit 25: don't allow 6 byte datalength
			('prena', c_long),           # bit 0: realtime preset enabled
								# bit 1: 
								# bit 2: sweep preset enabled
								# bit 3: ROI preset enabled
								# bit 4: Starts preset enabled
								# bit 5: ROI2 preset enabled
								# bit 6: ROI3 preset enabled
								# bit 7: ROI4 preset enabled
								# bit 8: ROI5 preset enabled
								# bit 9: ROI6 preset enabled
			('cycles', c_long),          # for sequential mode
			('sequences', c_long),       # 
			('syncout', c_long),         # LOWORD: sync out; bit 0..5 NIM syncout, bit 8..13 TTL syncout
								# bit7: NIM syncout_invert, bit15: TTL syncout_invert
								# 0="0", 1=10 MHz, 2=78.125 MHz, 3=100 MHz, 4=156.25 MHz,
								# 5=200 MHz, 6=312.5 MHz, 7=Ch0, 8=Ch1, 9=Ch2, 10=Ch3,
								# 11=Ch4, 12=Ch5, 13=GO, 14=Start_of_sweep, 15=Armed,
								# 16=SYS_ON, 17=WINDOW, 18=HOLD_OFF, 19=EOS_DEADTIME
								# 20=TIME[0],...,51=TIME[31], 52...63=SWEEP[0]..SWEEP[11]
								#
			('digio', c_long),           # LOWORD: Use of Dig I/O, GO Line:
								# bit 0: status dig 0..3
								# bit 1: Output digval and increment digval after stop
								# bit 2: Invert polarity
								# (bit 3: Push-Pull output, not possible)
								# bit 4..7:  Input pins 4..7 Trigger System 1..4
								# bit 8: GOWATCH
								# bit 9: GO High at Start
								# bit 10: GO Low at Stop
								# bit 11: Clear at triggered start
								# bit 12: Only triggered start
			('digval', c_long),			# digval=0..255 value for samplechanger
			('dac0', c_long),           #  DAC0 value (START) 
								#  bit 16: Start with rising edge
			('dac1', c_long),           #  DAC1 value (STOP 1) 
			('dac2', c_long),           #  DAC2 value (STOP 2)
			('dac3', c_long),           #  DAC3 value (STOP 3)
			('dac4', c_long),           #  DAC4 value (STOP 4)
			('dac5', c_long),           #  DAC5 value (STOP 5)
								# bit (14,15) of each word: 0=falling, 1=rising, 2=both, 3=both+CFT 
								# bit 17 of each: pulse width mode under threshold
			('fdac', c_int),				# Feature DAC 0..16383 --> 0..2.5V 
			('tagbits', c_int),          # number of tagbits
			('extclk', c_int),			# use external clock
			('maxchan', c_long),			# number of input channels (=6)
			('serno', c_long),			# serial number
			('ddruse', c_long),          # bit0: DDR_USE, bit1: DDR_2GB
								# bits[2:3]: usb_usage
								# bits[4:5]: wdlen
			('active', c_long),          # module in system
			('holdafter', c_double),	    # Hold off
			('swpreset', c_double),      # sweep preset value
			('fstchan', c_double),		# acquisition delay
			('timepreset', c_double)    # time preset
		]
	class ACQDEF(Structure):
		_fields_ = [
			('nDevices', c_int),          # Number of channels = number of modules * 6
			('nDisplays', c_int),         # Number of histograms = nDevices + Positions + Maps
			('nSystems', c_int),          # Number of independent systems = 1
			('bRemote', c_int),           # 1 if server controlled by MPANT
			('sys', c_uint),      # System definition word:
									# bit0=0, bit1=0: dev#0 in system 1
									# bit0=1, bit1=0: dev#0 in system 2
									# bit0=0, bit1=1: dev#0 in system 3
									# bit0=1, bit1=1: dev#0 in system 4
									# bit2..bit6: 
									# bit6=1, bit7=1: dev#3 in system 4 
			('sys0', (c_int*56)),           # (reserved:) System definition words for CHN1..18:
									# bit 0 CHN active
									# bit 1 =1 CHN coinc, =0 single
									# bit 2..4 CHN in system1..7
			('sys1', (c_int*56))           # (reserved:) CHN in System
		]

	class COINCDEF(Structure):
		_fields_ = [
			('adcnum', c_uint),     # Number of active ADC's (=0) 
			('tofnum', c_uint),     # Number of active TOF channels 
			('ntofs0', c_uint),	   # Number of TOF inputs 
			('modules', c_uint),    # Number of MCS6A modules
			('nadcs', c_uint),      # Number of ADCs (=0)

			('sys0', (c_int*56)),				# System definition words for ADCs (1..24):
									# see active definition in ADCSETTING
			('sys1', (c_int*56)),				# ADC in System (=1)
			('adcs', (c_int*8)),				# Number of ADCs per module (0)
			('tofs', (c_int*8)),				# Number of TOF inputs per module
			('res', (c_int*8))				# reserved
		]

	class ACQDATA(Structure):
		_fields_ = [
			('s0', POINTER(c_ulong)),          # pointer to spectrum
			('region', POINTER(c_ulong)),       # pointer to regions
			('comment0', POINTER(c_ubyte)),     # pointer to strings
			('cnt', POINTER(c_double)),                 # pointer to counters
			('hs0', wintypes.HANDLE),
			('hrg', wintypes.HANDLE),
			('hcm', wintypes.HANDLE),
			('hct', wintypes.HANDLE)
		]

	MAXCNT=448
	MAXDSP=64
	MAXDEV=3
	ID_SAVE=103
	ID_CONTINUE=106
	ID_START=109
	ID_BREAK=137
	ID_NEWSETTING=139
	ID_GETSTATUS=141
	ID_SAVEFILE=151
	ID_ERASE=154
	ID_LOADFILE=155
	ID_NEWDATA=160
	ID_HARDWDLG=161
	ID_SAVEFILE2=194
	ID_LOADFILE2=203
	ID_SAVEFILE3=217
	ID_LOADFILE3=219
	ID_SAVEFILE4=223
	ID_LOADFILE4=225
	ID_LOADFILE5=226
	ID_LOADFILE6=227
	ID_LOADFILE7=228
	ID_LOADFILE8=229
	ID_SAVEFILE5=230
	ID_SAVEFILE6=231
	ID_SAVEFILE7=232
	ID_SAVEFILE8=233
	ID_SUMFILE=234
	ID_SUMFILE2=235
	ID_SUMFILE3=236
	ID_SUMFILE4=237
	ID_SUMFILE5=238
	ID_SUMFILE6=239
	ID_SUMFILE7=240
	ID_SUMFILE8=241
	ID_LEDBLINK0=280
	ID_LEDBLINK1=281
	ID_LEDBLINK2=282
	ID_SUBTRACT=289
	ID_SMOOTH=290
	ID_SUBTRACT2=296
	ID_SMOOTH2=297
	ID_SUBTRACT3=298
	ID_SMOOTH3=299
	ID_SUBTRACT4=300
	ID_SMOOTH4=301
	ID_SUBTRACT5=302
	ID_SMOOTH5=303
	ID_SUBTRACT6=304
	ID_SMOOTH6=305
	ID_SUBTRACT7=306
	ID_SMOOTH7=307
	ID_SUBTRACT8=308
	ID_SMOOTH8=309
	ID_SAVEFILE9=310
	ID_SAVEFILE10=311
	ID_SAVEFILE11=312
	ID_SAVEFILE12=313
	ID_SAVEFILE13=314
	ID_SAVEFILE14=315
	ID_SAVEFILE15=316
	ID_SAVEFILE16=317
	ID_LOADFILE9=318
	ID_LOADFILE10=319
	ID_LOADFILE11=320
	ID_LOADFILE12=321
	ID_LOADFILE13=322
	ID_LOADFILE14=323
	ID_LOADFILE15=324
	ID_LOADFILE16=325
	ID_SUMFILE9=326
	ID_SUMFILE10=327
	ID_SUMFILE11=328
	ID_SUMFILE12=329
	ID_SUMFILE13=330
	ID_SUMFILE14=331
	ID_SUMFILE15=332
	ID_SUMFILE16=333
	ID_SUBTRACT9=334
	ID_SUBTRACT10=335
	ID_SUBTRACT11=336
	ID_SUBTRACT12=337
	ID_SUBTRACT13=338
	ID_SUBTRACT14=339
	ID_SUBTRACT15=340
	ID_SUBTRACT16=341
	ID_COMBDLG=401
	ID_DATADLG=402
	ID_MAPLSTDLG=403
	ID_REPLDLG=404
	ID_ERASE3=1109
	ID_ERASE4=1110
	ID_ERASEFILE2=1111
	ID_ERASEFILE3=1112
	ID_ERASEFILE4=1113
	ID_START2=1114
	ID_BREAK2=1115
	ID_CONTINUE2=1116
	ID_START3=1117
	ID_BREAK3=1118
	ID_CONTINUE3=1119
	ID_START4=1120
	ID_BREAK4=1121
	ID_CONTINUE4=1122
	ID_RUNCMD=1123
	ID_RUNCMD2=1124
	ID_RUNCMD3=1125
	ID_RUNCMD4=1126
	ID_RUNCMD5=1127
	ID_RUNCMD6=1128
	ID_RUNCMD7=1129
	ID_RUNCMD8=1130
	ID_ERASEFILE5=1131
	ID_ERASEFILE6=1132
	ID_ERASEFILE7=1133
	ID_ERASEFILE8=1134
	ID_DIGINOUT=1137
	ID_ERASE2=1164

#typedef int (WINAPI *IMPAGETSETTING) (ACQSETTING FAR *Setting, int nDisplay); # Get Spectra Settings stored in the DLL
	def GetSettingData(self, nDisplay):
		Setting=self.ACQSETTING()
		IMPAGETSETTING = self.dll.GetSettingData
		IMPAGETSETTING.restype = c_int
		IMPAGETSETTING.argtypes = [POINTER(self.ACQSETTING), c_int]
		return {'err':IMPAGETSETTING(byref(Setting), nDisplay), 'Setting':Setting}
# typedef int (WINAPI *IMPAGETSTATUS) (ACQSTATUS FAR *Status, int nDisplay); # Get the Status
	def GetStatusData(self, nDisplay):
		Status = self.ACQSTATUS()
		IMPAGETSTATUS = self.dll.GetStatusData
		IMPAGETSTATUS.restype = c_int
		IMPAGETSTATUS.argtypes = [POINTER(self.ACQSTATUS), c_int]
		return {'err':IMPAGETSTATUS(byref(Status), nDisplay), 'Status':Status}
# typedef VOID (WINAPI *IMPARUNCMD) (int nDisplay, LPSTR Cmd); # Executes command
	def RunCmd(self, nDisplay, Cmd):
		IMPARUNCMD = self.dll.RunCmd
		IMPARUNCMD.restype = c_void_p
		IMPARUNCMD.argtypes = [c_int, wintypes.LPSTR]
		return IMPARUNCMD(nDisplay, bytes(Cmd.encode()))
# typedef int (WINAPI *IMPAGETCNT) (double FAR *cntp, int nDisplay); # Copies Cnt numbers to an array
	def LVGetCnt(self, nDisplay):
		cntp = (c_double*self.MAXCNT)()
		IMPAGETCNT = self.dll.LVGetCnt
		IMPAGETCNT.restype = c_int
		IMPAGETCNT.argtypes = [POINTER(c_double), c_int]
		return {'err':IMPAGETCNT(byref(cntp), nDisplay), 'cntp':cntp}
# typedef int (WINAPI *IMPAGETROI) (unsigned long FAR *roip, int nDisplay); # Copies the ROI boundaries to an array
# roiboundarieslength = 2 * DLLSetting[nDisplay].nregions;
	def LVGetRoi(self, nDisplay):
		roiboundarieslength = 2*self.GetSettingData(nDisplay)['Setting'].nregions
		roip = (c_long*roiboundarieslength)()
		IMPAGETROI = self.dll.LVGetRoi
		IMPAGETROI.restype = c_int
		IMPAGETROI.argtypes = [POINTER(c_long), c_int]
		return {'err':IMPAGETROI(byref(roip), nDisplay),'roip':roip}
# typedef int (WINAPI *IMPAGETDEF) (ACQDEF FAR *Def); # Get System Definition
	def IMPAGETDEF(self):
		Def=self.ACQDEF()
		IMPAGETDEF = self.dll.IMPAGETDEF
		IMPAGETDEF.restype = c_int
		IMPAGETDEF.argtypes = [POINTER(self.ACQDEF)]
		return {'err':IMPAGETDEF(byref(Def)), 'Def':Def}
# typedef int (WINAPI *IMPAGETDAT) (unsigned long HUGE *datp, int nDisplay); # Copies the spectrum to an array
# spectrumlength is defined by the range of the scan
	def LVGetDat(self, nDisplay):
		spectrumlength = self.GetSettingData(nDisplay)['Setting'].range
		datp = (c_ulong*spectrumlength)()
		IMPAGETDAT = self.dll.LVGetDat
		IMPAGETDAT.restype = c_int
		IMPAGETDAT.argtypes = [POINTER(c_ulong), c_int]
		data = numpy.frombuffer(datp, dtype=numpy.dtype(c_ulong))
		return {'err':IMPAGETDAT(datp, nDisplay), 'data':data}
# typedef int (WINAPI *IMPAGETSTR) (char FAR *strp, int nDisplay); # Copies strings to an array
	stringlength=1024
	def LVGetStr(self, nDisplay):
		datp = (c_char*self.stringlength)()
		IMPAGETSTR = self.dll.LVGetStr
		IMPAGETSTR.restype = c_int
		IMPAGETSTR.argtypes = [POINTER(c_char), c_int]
		return {'err':IMPAGETSTR(byref(datp), nDisplay), 'datp':datp}
# typedef UINT (WINAPI *IMPASERVEXEC) (HWND ClientWnd);  # Register client at server MCS6.EXE
	def ServExec(self, ClientWnd):
		IMPASERVEXEC = self.dll.ServExec
		IMPASERVEXEC.restype = c_uint
		IMPASERVEXEC.argtypes = [wintypes.HWND]
		return IMPASERVEXEC(ClientWnd)
# typedef int (WINAPI *IMPANEWSTATUS) (int nDev);# Request actual Status from Server
	def GetStatus(self, nDev):
		IMPANEWSTATUS = self.dll.GetStatus
		IMPANEWSTATUS.restype = c_int
		IMPANEWSTATUS.argtypes = [c_int]
		return IMPANEWSTATUS(nDev)
# typedef int (WINAPI *IMPAGETMCSSET) (BOARDSETTING *Board, int nDevice); # Get MCSSettings from DLL
	def GetMCSSetting(self, nDevice):
		Board = self.BOARDSETTING()
		IMPAGETMCSSET = self.dll.GetMCSSetting
		IMPAGETMCSSET.restype = c_int
		IMPAGETMCSSET.argtypes = [POINTER(self.BOARDSETTING), c_int]
		return {'err':IMPAGETMCSSET(byref(Board), nDevice), 'Board':Board}
# typedef int (WINAPI *IMPAGETDATSET) (DATSETTING *Defdat); # Get Data Format Definition from DLL
	def GetDatSetting(self):
		Defdat = self.DATSETTING()
		IMPAGETDATSET = self.dll.GetDatSetting
		IMPAGETDATSET.restype = c_int
		IMPAGETDATSET.argtypes = [POINTER(self.DATSETTING)]
		return {'err':IMPAGETDATSET(byref(Defdat)), 'Defdat':Defdat}
# typedef int (WINAPI *IMPADIGINOUT) (int value, int enable);  # controls Dig I/0 , # returns digin
	def DigInOut(self, value, enable):
		IMPADIGINOUT = self.dll.DigInOut
		IMPADIGINOUT.restype = c_int
		IMPADIGINOUT.argtypes = [c_int, c_int]
		return IMPADIGINOUT(value, enable)
# typedef int (WINAPI *IMPADACOUT) (int value);# output Dac value as analogue voltage
	def DacOut(self, value):
		IMPADACOUT = self.dll.DacOut
		IMPADACOUT.restype = c_int
		IMPADACOUT.argtypes = [c_int]
		return IMPADACOUT(value)
# typedef VOID (WINAPI *IMPASTART) (int nSystem);# Start
	def Start(self, nSystem):
		IMPASTART = self.dll.Start
		IMPASTART.restype = c_void_p
		IMPASTART.argtypes = [c_int]
		return IMPASTART(nSystem)
# typedef VOID (WINAPI *IMPAHALT) (int nSystem);# Halt
	def Halt(self, nSystem):
		IMPAHALT = self.dll.Halt
		IMPAHALT.restype = c_void_p
		IMPAHALT.argtypes = [c_int]
		return IMPAHALT(nSystem)
# typedef VOID (WINAPI *IMPACONTINUE) (int nSystem);# Continue
	def Continue(self, nSystem):
		IMPACONTINUE = self.dll.Continue
		IMPACONTINUE.restype = c_void_p
		IMPACONTINUE.argtypes = [c_int]
		return IMPACONTINUE(nSystem)
# typedef VOID (WINAPI *IMPAERASE) (int nSystem);# Erase spectrum
	def Erase(self, nSystem):
		IMPAERASE = self.dll.Erase
		IMPAERASE.restype = c_void_p
		IMPAERASE.argtypes = [c_int]
		return IMPAERASE(nSystem)