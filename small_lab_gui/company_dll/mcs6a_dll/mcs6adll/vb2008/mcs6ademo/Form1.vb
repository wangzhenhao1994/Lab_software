Imports mcs6ademo.MCS6VB
Public Class Form1
    Dim Sysno As Integer
    Dim Status As mcs6ademo.MCS6VB.MCS6IO.Acqstatus
    Dim Setting As mcs6ademo.MCS6VB.MCS6IO.Acqsetting
    Dim Dsetting As mcs6ademo.MCS6VB.MCS6IO.Datsetting
    Dim Msetting As mcs6ademo.MCS6VB.MCS6IO.Boardsetting
    Dim OldStarted As Integer
    Dim Mcano As Integer
    Dim Chan As Integer
    Dim Hist(24) As Integer
    Dim Toggle As Integer
    Dim Ret As Integer
    Dim ccc(2048) As Char
    Dim bcc(256) As Char
    Dim scc(256) As Short

    Private Sub UpdateStatus()
        LabelStarted.Text = Status.Started
        LabelMaxval.Text = Status.Maxval
        LabelRuntime.Text = Status.Cnt0
        LabelOfls.Text = Status.Cnt1
        LabelTotalsum.Text = Status.Cnt2
        LabelRoisum.Text = Status.Cnt3
        LabelRoirate.Text = Format$(Status.Cnt4, "######0.0#")
        LabelSweeps.Text = Status.Cnt5
        LabelStarts.Text = Status.Cnt6
    End Sub
    Private Sub UpdateSetting()
        LabelRange.Text = Setting.Range
        LabelCftfak.Text = Setting.Cftfak
        LabelRoimin.Text = Setting.Roimin
        LabelRoimax.Text = Setting.Roimax
        LabelNregions.Text = Setting.Nregions
        LabelCaluse.Text = Setting.Caluse
        LabelCalpoints.Text = Setting.Calpoints
        LabelParam.Text = Setting.Param
        LabelOffset.Text = Setting.Offset
        LabelXdim.Text = Setting.Xdim
        LabelBitshift.Text = Setting.Bitshift
        LabelActive.Text = Setting.Active
        LabelEventpreset.Text = Setting.Eventpreset
    End Sub
    Private Sub UpdateBoardsetting()
        LabelSweepmode.Text = Msetting.Sweepmode
        LabelPrena.Text = Msetting.Prena
        LabelCycles.Text = Msetting.Cycles
        LabelSequences.Text = Msetting.Sequences
        LabelSyncout.Text = Msetting.Syncout
        LabelDigio.Text = Msetting.Digio
        LabelDigval.Text = Msetting.Digval
        LabelDac0.Text = Msetting.Dac0
        LabelDac1.Text = Msetting.Dac1
        LabelDac2.Text = Msetting.Dac2
        LabelDac3.Text = Msetting.Dac3
        LabelDac4.Text = Msetting.Dac4
        LabelDac5.Text = Msetting.Dac5
        LabelFdac.Text = Msetting.Fdac
        LabelTagbits.Text = Msetting.Tagbits
        LabelExtclk.Text = Msetting.Extclk
        LabelSerno.Text = Msetting.Serno
        LabelDdruse.Text = Msetting.Ddruse
        LabelHoldafter.Text = Msetting.Holdafter
        LabelSwpreset.Text = Msetting.Swpreset
        LabelFstchan.Text = Msetting.Fstchan
        LabelTimepreset.Text = Msetting.Timepreset
    End Sub

    Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
        OldStarted = 0
        Mcano = 1
        Sysno = 0
        Chan = 0
        Ret = mcs6ademo.MCS6VB.MCS6IO.ServExec(0)
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetStatus(0)
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetStatusData(Status, 0)
        Call UpdateStatus()
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetSettingData(Setting, 0)
        Call UpdateSetting()
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetMCSSetting(Msetting, 0)
        Call UpdateBoardsetting()
    End Sub


    Private Sub CommandDatasettings_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandDatasettings.Click
        Dim n As Integer
        Call mcs6ademo.MCS6VB.MCS6IO.GetDatSetting(Dsetting)
        LabelSavedata.Text = Dsetting.SaveData
        LabelAutoinc.Text = Dsetting.Autoinc
        LabelFmt.Text = Dsetting.Fmt
        LabelMpafmt.Text = Dsetting.Mpafmt
        LabelSephead.Text = Dsetting.Sephead
        LabelSmpts.Text = Dsetting.Smpts
        LabelAddcal.Text = Dsetting.Caluse
        n = mcs6ademo.MCS6VB.MCS6IO.BytearrayToShortarray(scc(0), Dsetting.Filename, 256)
        For index As Integer = 0 To n
            bcc(index) = Chr(scc(index))
        Next
        LabelMpafilename.Text = bcc
        n = mcs6ademo.MCS6VB.MCS6IO.BytearrayToShortarray(scc(0), Dsetting.Specfile, 256)
        For index As Integer = 0 To n
            bcc(index) = Chr(scc(index))
        Next
        LabelSpecfile.Text = bcc
        n = mcs6ademo.MCS6VB.MCS6IO.BytearrayToShortarray(scc(0), Dsetting.Command, 256)
        For index As Integer = 0 To n
            bcc(index) = Chr(scc(index))
        Next
        LabelCommand.Text = bcc
    End Sub

    Private Sub GetMcano()
        Mcano = Val(TextMC.Text)
        If Mcano < 1 Then
            Mcano = 1
            TextMC.Text = Mcano
        End If
        If Mcano > 6 Then
            Mcano = 6
            TextMC.Text = Mcano
        End If
    End Sub
    Private Sub GetChan()
        Chan = Val(TextChan.Text)
        If Chan > Setting.Range - 25 Then
            Chan = Setting.Range - 25
            TextChan.Text = Chan
        End If
        If Chan < 0 Then
            Chan = 0
            TextChan.Text = Chan
        End If
    End Sub
    Private Sub CommandExecute_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandExecute.Click
        Dim cmd As String
        Dim c(256) As Byte
        Dim ccs As Short
        cmd = "                                                                                                                     "
        Mid$(cmd, 1) = TextCommand.Text
        bcc = cmd
        For index As Integer = 0 To 100
            ccs = Asc(bcc(index))
            c(index) = ccs
        Next

        Call mcs6ademo.MCS6VB.MCS6IO.RunCmd(0, c(0))
        For index As Integer = 0 To 100
            ccs = c(index)
            bcc(index) = Chr(ccs)
        Next
        cmd = bcc

        TextRespons.Text = cmd
        Call GetMcano()
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetStatus(Mcano - 1)
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetStatusData(Status, Mcano - 1)
        Call UpdateStatus()
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetSettingData(Setting, Mcano - 1)
        Call UpdateSetting()
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetMCSSetting(Msetting, 0)
        Call UpdateBoardsetting()
    End Sub

    Private Sub CommandGetspec_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandGetspec.Click
        Call GetMcano()
        Call GetChan()
        Call mcs6ademo.MCS6VB.MCS6IO.GetBlock(Hist(0), Chan, Chan + 24, 1, Mcano - 1)
        LabelData0.Text = Hist(0)
        LabelData1.Text = Hist(1)
        LabelData2.Text = Hist(2)
        LabelData3.Text = Hist(3)
        LabelData4.Text = Hist(4)
        LabelData5.Text = Hist(5)
        LabelData6.Text = Hist(6)
        LabelData7.Text = Hist(7)
        LabelData8.Text = Hist(8)
        LabelData9.Text = Hist(9)
        LabelData10.Text = Hist(10)
        LabelData11.Text = Hist(11)
        LabelData12.Text = Hist(12)
        LabelData13.Text = Hist(13)
        LabelData14.Text = Hist(14)
        LabelData15.Text = Hist(15)
        LabelData16.Text = Hist(16)
        LabelData17.Text = Hist(17)
        LabelData18.Text = Hist(18)
        LabelData19.Text = Hist(19)
        LabelData20.Text = Hist(20)
        LabelData21.Text = Hist(21)
        LabelData22.Text = Hist(22)
        LabelData23.Text = Hist(23)
    End Sub

    Private Sub CommandGetstring_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandGetstring.Click
        Dim b As String
        Dim c(2048) As Byte
        Dim ccs As Short
        b = "                                                                                                                     "
        Call GetMcano()
        Ret = mcs6ademo.MCS6VB.MCS6IO.LVGetStr(c(0), Mcano - 1)

        For index As Integer = 0 To 2047
            ccs = c(index)
            ccc(index) = Chr(ccs)
        Next
        b = ccc
        LabelLine0.Text = Mid$(b, 1, 60)
        LabelLine1.Text = Mid$(b, 61, 60)
        LabelLine2.Text = Mid$(b, 121, 60)
        LabelLine3.Text = Mid$(b, 181, 60)
        LabelLine4.Text = Mid$(b, 241, 60)
        LabelLine5.Text = Mid$(b, 301, 60)
        LabelLine6.Text = Mid$(b, 361, 60)
        LabelLine7.Text = Mid$(b, 421, 60)
        LabelLine8.Text = Mid$(b, 481, 60)
        LabelLine9.Text = Mid$(b, 541, 60)
        LabelLine10.Text = Mid$(b, 601, 60)
        LabelLine11.Text = Mid$(b, 881, 60)
        LabelLine12.Text = Mid$(b, 961, 60)
        LabelLine13.Text = Mid$(b, 661, 100)
    End Sub

    Private Sub CommandErase_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandErase.Click
        Call mcs6ademo.MCS6VB.MCS6IO.EraseData(0)
    End Sub
    Private Sub CommandHalt_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandHalt.Click
        Call mcs6ademo.MCS6VB.MCS6IO.Halt(0)
    End Sub

    Private Sub CommandSave_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandSave.Click
        Call mcs6ademo.MCS6VB.MCS6IO.SaveData(0, 1)
    End Sub

    Private Sub CommandStart_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandStart.Click
        Call mcs6ademo.MCS6VB.MCS6IO.Start(0)
    End Sub
    Private Sub CommandContinue_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandContinue.Click
        Call mcs6ademo.MCS6VB.MCS6IO.Cont(0)
    End Sub
    Private Sub CommandSetting_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandSetting.Click
        Call GetMcano()
        If mcs6ademo.MCS6VB.MCS6IO.GetSettingData(Setting, Mcano - 1) = 1 Then
            Call UpdateSetting()
        End If
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetMCSSetting(Msetting, 0)
        Call UpdateBoardsetting()
    End Sub

    Private Sub CommandUpdate_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles CommandUpdate.Click
        Call GetMcano()
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetStatus(Mcano - 1)
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetStatusData(Status, Mcano - 1)
        Call UpdateStatus()
    End Sub

    Private Sub Timer1_Tick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Timer1.Tick
        Call GetMcano()
        Ret = mcs6ademo.MCS6VB.MCS6IO.GetStatus(Mcano - 1)
        If mcs6ademo.MCS6VB.MCS6IO.GetStatusData(Status, Mcano - 1) = 1 Then
            If Status.Started = 1 Or OldStarted = 1 Then
                Toggle = Not Toggle
                OldStarted = Status.Started
                Call UpdateStatus()
            End If
        End If
        Call UpdateStatus()
    End Sub
End Class
