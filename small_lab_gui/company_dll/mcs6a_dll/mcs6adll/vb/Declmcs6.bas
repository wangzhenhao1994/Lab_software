Attribute VB_Name = "DECLMCS6"
Type Acqstatus
    Val As Long
    Val1 As Long
    Cnt(0 To 7) As Double
End Type

Type Acqsetting
    Range As Long
    Cftfak As Long
    Roimin As Long
    Roimax As Long
    Nregions As Long
    Caluse As Long
    Calpoints As Long
    Param As Long
    Offset As Long
    Xdim As Long
    Bitshift As Long
    Active As Long
    Roipreset As Double
    Dummy1 As Double
    Dummy2 As Double
    Dummy3 As Double
End Type

Type Replaysetting
    Use As Long
    Modified As Long
    Limit As Long
    Speed As Long
    Startsfrom As Double
    Startsto As Double
    Startspreset As Double
    Filename As String * 256
End Type

Type Datsetting
    SaveData As Long
    Autoinc As Long
    Fmt As Long
    Mpafmt As Long
    Sephead As Long
    Smpts As Long
    Caluse As Long
    Filename As String * 256
    Specfile As String * 256
    Command As String * 256
End Type

Type Boardsetting
    Sweepmode As Long
    Prena As Long
    Cycles As Long
    Sequences As Long
    Syncout As Long
    Digio As Long
    Digval As Long
    Dac0 As Long
    Dac1 As Long
    Dac2 As Long
    Dac3 As Long
    Dac4 As Long
    Dac5 As Long
    Fdac As Long
    Tagbits As Long
    Extclk As Long
    Maxchan As Long
    Serno As Long
    Ddruse As Long
    Active As Long
    Holdafter As Double
    Swpreset As Double
    Fstchan As Double
    Timepreset As Double
End Type

Type Acqdef
  Ndevices As Long
  Ndisplays As Long
  Nsystems As Long
  Bremote As Long
  Sys As Long
  Sys0(56) As Long
  Sys1(56) As Long
End Type

Declare Sub StoreSettingData Lib "DMCS6.DLL" Alias "#2" (Setting As Acqsetting, ByVal Ndisplay As Long)
Declare Function GetSettingData Lib "DMCS6.DLL" Alias "#3" (Setting As Acqsetting, ByVal Ndisplay As Long) As Long
Declare Function GetStatusData Lib "DMCS6.DLL" Alias "#5" (Status As Acqstatus, ByVal Ndevice As Long) As Long
Declare Sub Start Lib "DMCS6.DLL" Alias "#6" (ByVal Nsystem As Long)
Declare Sub Halt Lib "DMCS6.DLL" Alias "#7" (ByVal Nsystem As Long)
Declare Sub Continue Lib "DMCS6.DLL" Alias "#8" (ByVal Nsystem As Long)
Declare Sub NewSetting Lib "DMCS6.DLL" Alias "#9" (ByVal Ndisplay As Long)
Declare Function ServExec Lib "DMCS6.DLL" Alias "#10" (ByVal Clwnd As Long) As Long
Declare Function GetSpec Lib "DMCS6.DLL" Alias "#13" (ByVal I As Long, ByVal Ndisplay As Long) As Long
Declare Sub SaveSetting Lib "DMCS6.DLL" Alias "#14" ()
Declare Function GetStatus Lib "DMCS6.DLL" Alias "#15" (ByVal Ndevice As Long) As Long
Declare Sub EraseData Lib "DMCS6.DLL" Alias "#16" (ByVal Nsystem As Long)
Declare Sub SaveData Lib "DMCS6.DLL" Alias "#17" (ByVal Ndevice As Long, ByVal All As Long)
Declare Sub GetBlock Lib "DMCS6.DLL" Alias "#18" (Hist As Long, ByVal Start As Long, ByVal Size As Long, ByVal Stp As Long, ByVal Ndisplay As Long)
Declare Function GetDefData Lib "DMCS6.DLL" Alias "#20" (Def As Acqdef) As Long
Declare Sub LoadData Lib "DMCS6.DLL" Alias "#21" (ByVal Ndevice As Long, ByVal All As Long)
Declare Sub NewData Lib "DMCS6.DLL" Alias "#22" ()
Declare Sub HardwareDlg Lib "DMCS6.DLL" Alias "#23" (ByVal Item As Long)
Declare Sub UnregisterClient Lib "LMCS6.DLL" Alias "#24" ()
Declare Sub DestroyClient Lib "DMCS6.DLL" Alias "#25" ()
Declare Sub RunCmd Lib "DMCS6.DLL" Alias "#28" (ByVal Ndevice As Long, ByVal Cmd As String)
Declare Sub AddData Lib "DMCS6.DLL" Alias "#29" (ByVal Ndisplay As Long, ByVal All As Long)
Declare Function LVGetRoi Lib "DMCS6.DLL" Alias "#30" (Roi As Long, ByVal Ndisplay As Long) As Long
Declare Function LVGetCnt Lib "DMCS6.DLL" Alias "#31" (Cnt As Double, ByVal Ndisplay As Long) As Long
Declare Function LVGetOneCnt Lib "DMCS6.DLL" Alias "#32" (Cnt As Double, ByVal Ndisplay As Long, ByVal Cntnum As Long) As Long
Declare Function LVGetStr Lib "DMCS6.DLL" Alias "#33" (ByVal Comment As String, ByVal Ndisplay As Long) As Long
Declare Sub SubData Lib "DMCS6.DLL" Alias "#34" (ByVal Ndisplay As Long, ByVal All As Long)
Declare Sub Smooth Lib "DMCS6.DLL" Alias "#35" (ByVal Ndisplay As Long)
Declare Function GetMCSSetting Lib "DMCS6.DLL" Alias "#39" (Msetting As Boardsetting) As Long
Declare Function GetDatSetting Lib "DMCS6.DLL" Alias "#41" (Dsetting As Datsetting) As Long
Declare Function GetReplaySetting Lib "DMCS6.DLL" Alias "#43" (Rsetting As Replaysetting) As Long

