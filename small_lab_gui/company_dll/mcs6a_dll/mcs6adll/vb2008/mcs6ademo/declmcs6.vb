'Attribute VB_Name = "DECLMCS6"
Imports System
Imports System.Runtime.InteropServices

Namespace MCS6VB
    Public Class MCS6IO
        Structure Acqstatus
            Public Started As Integer
            Public Maxval As Integer
            Public Cnt0 As Double
            Public Cnt1 As Double
            Public Cnt2 As Double
            Public Cnt3 As Double
            Public Cnt4 As Double
            Public Cnt5 As Double
            Public Cnt6 As Double
            Public Cnt7 As Double
        End Structure

        Structure Acqsetting
            Public Range As Integer
            Public Cftfak As Integer
            Public Roimin As Integer
            Public Roimax As Integer
            Public Nregions As Integer
            Public Caluse As Integer
            Public Calpoints As Integer
            Public Param As Integer
            Public Offset As Integer
            Public Xdim As Integer
            Public Bitshift As Integer
            Public Active As Integer
            Public Eventpreset As Double
            Public Dummy1 As Double
            Public Dummy2 As Double
            Public Dummy3 As Double
        End Structure

        <StructLayout(LayoutKind.Explicit, Size:=296, CharSet:=CharSet.Ansi)> _
        Structure Replaysetting
            <FieldOffset(0)> Public Use As Integer
            <FieldOffset(4)> Public Modified As Integer
            <FieldOffset(8)> Public Limit As Integer
            <FieldOffset(12)> Public Speed As Integer
            <FieldOffset(16)> Public Startsfrom As Double
            <FieldOffset(24)> Public Startsto As Double
            <FieldOffset(32)> Public Startspreset As Double
            <FieldOffset(40)> Public Filename As Byte
        End Structure

        <StructLayout(LayoutKind.Explicit, Size:=796, CharSet:=CharSet.Ansi)> _
        Structure Datsetting
            <FieldOffset(0)> Public SaveData As Integer
            <FieldOffset(4)> Public Autoinc As Integer
            <FieldOffset(8)> Public Fmt As Integer
            <FieldOffset(12)> Public Mpafmt As Integer
            <FieldOffset(16)> Public Sephead As Integer
            <FieldOffset(20)> Public Smpts As Integer
            <FieldOffset(24)> Public Caluse As Integer
            <FieldOffset(28)> Public Filename As Byte
            <FieldOffset(284)> Public Specfile As Byte
            <FieldOffset(540)> Public Command As Byte
        End Structure

        Structure Boardsetting
            Public Sweepmode As Integer
            Public Prena As Integer
            Public Cycles As Integer
            Public Sequences As Integer
            Public Syncout As Integer
            Public Digio As Integer
            Public Digval As Integer
            Public Dac0 As Integer
            Public Dac1 As Integer
            Public Dac2 As Integer
            Public Dac3 As Integer
            Public Dac4 As Integer
            Public Dac5 As Integer
            Public Fdac As Integer
            Public Tagbits As Integer
            Public Extclk As Integer
            Public Maxchan As Integer
            Public Serno As Integer
            Public Ddruse As Integer
            Public Active As Integer
            Public Holdafter As Double
            Public Swpreset As Double
            Public Fstchan As Double
            Public Timepreset As Double
        End Structure

        <StructLayout(LayoutKind.Explicit, Size:=468, CharSet:=CharSet.Ansi)> _
        Structure Acqdef
            <FieldOffset(0)> Public Ndevices As Integer
            <FieldOffset(4)> Public Ndisplays As Integer
            <FieldOffset(8)> Public Nsystems As Integer
            <FieldOffset(12)> Public Bremote As Integer
            <FieldOffset(16)> Public Auxsys As Integer
            <FieldOffset(20)> Public Sys0 As Integer
            <FieldOffset(244)> Public Sys1 As Integer
        End Structure

        Declare Sub StoreSettingData Lib "DMCS6.DLL" Alias "#2" (ByRef Setting As Acqsetting, ByVal Ndisplay As Integer)
        Declare Function GetSettingData Lib "DMCS6.DLL" Alias "#3" (ByRef Setting As Acqsetting, ByVal Ndisplay As Integer) As Integer
        Declare Function GetStatusData Lib "DMCS6.DLL" Alias "#5" (ByRef Status As Acqstatus, ByVal Ndevice As Integer) As Integer
        Declare Sub Start Lib "DMCS6.DLL" Alias "#6" (ByVal Nsystem As Integer)
        Declare Sub Halt Lib "DMCS6.DLL" Alias "#7" (ByVal Nsystem As Integer)
        Declare Sub Cont Lib "DMCS6.DLL" Alias "#8" (ByVal Nsystem As Integer)
        Declare Sub NewSetting Lib "DMCS6.DLL" Alias "#9" (ByVal Ndisplay As Integer)
        Declare Function ServExec Lib "DMCS6.DLL" Alias "#10" (ByVal Clwnd As Integer) As Integer
        Declare Function GetSpec Lib "DMCS6.DLL" Alias "#13" (ByVal I As Integer, ByVal Ndisplay As Integer) As Integer
        Declare Sub SaveSetting Lib "DMCS6.DLL" Alias "#14" ()
        Declare Function GetStatus Lib "DMCS6.DLL" Alias "#15" (ByVal Ndevice As Integer) As Integer
        Declare Sub EraseData Lib "DMCS6.DLL" Alias "#16" (ByVal Nsystem As Integer)
        Declare Sub SaveData Lib "DMCS6.DLL" Alias "#17" (ByVal Ndevice As Integer, ByVal All As Integer)
        Declare Sub GetBlock Lib "DMCS6.DLL" Alias "#18" (ByRef Hist As Integer, ByVal Start As Integer, ByVal Size As Integer, ByVal Stp As Integer, ByVal Ndisplay As Integer)
        Declare Function GetDefData Lib "DMCS6.DLL" Alias "#20" (ByRef Def As Acqdef) As Integer
        Declare Sub LoadData Lib "DMCS6.DLL" Alias "#21" (ByVal Ndevice As Integer, ByVal All As Integer)
        Declare Sub NewData Lib "DMCS6.DLL" Alias "#22" ()
        Declare Sub HardwareDlg Lib "DMCS6.DLL" Alias "#23" (ByVal Item As Integer)
        Declare Sub UnregisterClient Lib "DMCS6.DLL" Alias "#24" ()
        Declare Sub DestroyClient Lib "DMCS6.DLL" Alias "#25" ()
        Declare Sub RunCmd Lib "DMCS6.DLL" Alias "#28" (ByVal Ndevice As Integer, ByRef Cmd As Byte)
        Declare Sub AddData Lib "DMCS6.DLL" Alias "#29" (ByVal Ndisplay As Integer, ByVal All As Integer)
        Declare Function LVGetRoi Lib "DMCS6.DLL" Alias "#30" (ByRef Roi As Integer, ByVal Ndisplay As Integer) As Integer
        Declare Function LVGetCnt Lib "DMCS6.DLL" Alias "#31" (ByRef Cnt As Double, ByVal Ndisplay As Integer) As Integer
        Declare Function LVGetOneCnt Lib "DMCS6.DLL" Alias "#32" (ByRef Cnt As Double, ByVal Ndisplay As Integer, ByVal Cntnum As Integer) As Integer
        Declare Function LVGetStr Lib "DMCS6.DLL" Alias "#33" (ByRef Comment As Byte, ByVal Ndisplay As Integer) As Integer
        Declare Sub SubData Lib "DMCS6.DLL" Alias "#34" (ByVal Ndisplay As Integer, ByVal All As Integer)
        Declare Sub Smooth Lib "DMCS6.DLL" Alias "#35" (ByVal Ndisplay As Integer)
        Declare Function GetMCSSetting Lib "DMCS6.DLL" Alias "#39" (ByRef Msetting As Boardsetting, ByVal Ndev As Integer) As Integer
        Declare Function GetDatSetting Lib "DMCS6.DLL" Alias "#41" (ByRef Dsetting As Datsetting) As Integer
        Declare Function GetReplaySetting Lib "DMCS6.DLL" Alias "#43" (ByRef Rsetting As Replaysetting) As Integer
        Declare Function BytearrayToShortarray Lib "DMCS6.DLL" Alias "#49" (ByRef Shortarray As Short, ByRef Bytearray As Byte, ByVal Length As Integer) As Integer
    End Class
End Namespace
