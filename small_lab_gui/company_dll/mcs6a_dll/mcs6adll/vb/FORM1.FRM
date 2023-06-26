VERSION 5.00
Begin VB.Form Form1 
   Appearance      =   0  'Flat
   BackColor       =   &H80000005&
   Caption         =   "MCS6A Demo"
   ClientHeight    =   8220
   ClientLeft      =   1230
   ClientTop       =   1680
   ClientWidth     =   10725
   BeginProperty Font 
      Name            =   "MS Sans Serif"
      Size            =   8.25
      Charset         =   0
      Weight          =   700
      Underline       =   0   'False
      Italic          =   0   'False
      Strikethrough   =   0   'False
   EndProperty
   ForeColor       =   &H80000008&
   Icon            =   "FORM1.frx":0000
   LinkTopic       =   "Form1"
   PaletteMode     =   1  'UseZOrder
   ScaleHeight     =   8220
   ScaleWidth      =   10725
   Begin VB.CommandButton CommandDatasettings 
      Appearance      =   0  'Flat
      Caption         =   "Get Datasettings"
      Height          =   255
      Left            =   4680
      TabIndex        =   99
      Top             =   4440
      Width           =   1935
   End
   Begin VB.CommandButton CommandGetstring 
      Appearance      =   0  'Flat
      Caption         =   "Get Strings"
      Height          =   255
      Left            =   2520
      TabIndex        =   59
      Top             =   3360
      Width           =   1935
   End
   Begin VB.CommandButton CommandGetspec 
      Appearance      =   0  'Flat
      Caption         =   "Get Spectrum"
      Height          =   255
      Left            =   8640
      TabIndex        =   43
      Top             =   120
      Width           =   1935
   End
   Begin VB.TextBox TextChan 
      Height          =   285
      Left            =   8640
      TabIndex        =   42
      Text            =   "0"
      Top             =   480
      Width           =   615
   End
   Begin VB.CommandButton CommandSetting 
      Appearance      =   0  'Flat
      Caption         =   "Update Setting"
      Height          =   255
      Left            =   6360
      TabIndex        =   18
      Top             =   120
      Width           =   1935
   End
   Begin VB.TextBox TextMC 
      Height          =   285
      Left            =   5640
      TabIndex        =   17
      Text            =   "0"
      Top             =   120
      Width           =   495
   End
   Begin VB.CommandButton CommandUpdate 
      Appearance      =   0  'Flat
      Caption         =   "Update Status"
      Height          =   255
      Left            =   1800
      TabIndex        =   15
      Top             =   120
      Width           =   1935
   End
   Begin VB.CommandButton CommandExecute 
      Appearance      =   0  'Flat
      Caption         =   "E&xecute"
      Height          =   255
      Left            =   240
      TabIndex        =   10
      Top             =   3720
      Width           =   855
   End
   Begin VB.TextBox TextCommand 
      Appearance      =   0  'Flat
      Height          =   285
      Left            =   240
      TabIndex        =   9
      Text            =   "RUN TEST.CTL"
      Top             =   4080
      Width           =   1935
   End
   Begin VB.CommandButton CommandSave 
      Appearance      =   0  'Flat
      Caption         =   "S&ave"
      Height          =   255
      Left            =   240
      TabIndex        =   8
      Top             =   2160
      Width           =   975
   End
   Begin VB.CommandButton CommandErase 
      Appearance      =   0  'Flat
      Caption         =   "&Erase"
      Height          =   255
      Left            =   240
      TabIndex        =   7
      Top             =   1800
      Width           =   975
   End
   Begin VB.Timer Timer1 
      Interval        =   500
      Left            =   0
      Top             =   120
   End
   Begin VB.CommandButton CommandContinue 
      Appearance      =   0  'Flat
      Caption         =   "&Continue"
      Height          =   255
      Left            =   240
      TabIndex        =   2
      Top             =   1440
      Width           =   975
   End
   Begin VB.CommandButton CommandHalt 
      Appearance      =   0  'Flat
      Caption         =   "&Halt"
      Height          =   255
      Left            =   240
      TabIndex        =   1
      Top             =   1080
      Width           =   975
   End
   Begin VB.CommandButton CommandStart 
      Appearance      =   0  'Flat
      Caption         =   "&Start"
      Height          =   255
      Left            =   240
      TabIndex        =   0
      Top             =   720
      Width           =   975
   End
   Begin VB.Label LabelCommand 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   119
      Top             =   6960
      Width           =   3135
   End
   Begin VB.Label Label43 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Command:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   118
      Top             =   6960
      Width           =   855
   End
   Begin VB.Label Labelspecfile 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   117
      Top             =   6720
      Width           =   3135
   End
   Begin VB.Label Label42 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Specfile:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   116
      Top             =   6720
      Width           =   855
   End
   Begin VB.Label LabelMpafilename 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   115
      Top             =   6480
      Width           =   3135
   End
   Begin VB.Label Label41 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Filename:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   114
      Top             =   6480
      Width           =   855
   End
   Begin VB.Label LabelAddcal 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   113
      Top             =   6240
      Width           =   975
   End
   Begin VB.Label Label40 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Caluse:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   112
      Top             =   6240
      Width           =   855
   End
   Begin VB.Label LabelSmpts 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   111
      Top             =   6000
      Width           =   975
   End
   Begin VB.Label Label38 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Smpts:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   110
      Top             =   6000
      Width           =   855
   End
   Begin VB.Label LabelSephead 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   109
      Top             =   5760
      Width           =   975
   End
   Begin VB.Label Label37 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Sephead:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   108
      Top             =   5760
      Width           =   855
   End
   Begin VB.Label LabelMpafmt 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   107
      Top             =   5520
      Width           =   975
   End
   Begin VB.Label Label35 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Mpafmt:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   106
      Top             =   5520
      Width           =   855
   End
   Begin VB.Label LabelFmt 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   105
      Top             =   5280
      Width           =   975
   End
   Begin VB.Label Label32 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Fmt:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   104
      Top             =   5280
      Width           =   855
   End
   Begin VB.Label LabelAutoinc 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   103
      Top             =   5040
      Width           =   975
   End
   Begin VB.Label Label29 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Autoinc:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   102
      Top             =   5040
      Width           =   855
   End
   Begin VB.Label LabelSavedata 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   5640
      TabIndex        =   101
      Top             =   4800
      Width           =   975
   End
   Begin VB.Label Label28 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Savedata:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   100
      Top             =   4800
      Width           =   855
   End
   Begin VB.Label LabelTotalrate 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4920
      TabIndex        =   98
      Top             =   1680
      Width           =   975
   End
   Begin VB.Label Label26 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Rate:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   3960
      TabIndex        =   97
      Top             =   1680
      Width           =   855
   End
   Begin VB.Label LabelRoisum 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4920
      TabIndex        =   96
      Top             =   1440
      Width           =   975
   End
   Begin VB.Label Label25 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Roisum:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   3960
      TabIndex        =   95
      Top             =   1440
      Width           =   855
   End
   Begin VB.Label LabelTotalsum 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4920
      TabIndex        =   94
      Top             =   1200
      Width           =   975
   End
   Begin VB.Label Label24 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Totalsum:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   3960
      TabIndex        =   93
      Top             =   1200
      Width           =   855
   End
   Begin VB.Label LabelOfls 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4920
      TabIndex        =   92
      Top             =   720
      Width           =   975
   End
   Begin VB.Label Label22 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Datalosts:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   3960
      TabIndex        =   91
      Top             =   720
      Width           =   855
   End
   Begin VB.Label LabelMaxval 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4920
      TabIndex        =   90
      Top             =   480
      Width           =   975
   End
   Begin VB.Label Label21 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Maxval:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   3960
      TabIndex        =   89
      Top             =   480
      Width           =   855
   End
   Begin VB.Label LabelRoimax 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   88
      Top             =   1200
      Width           =   975
   End
   Begin VB.Label Label8 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Roimax:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   87
      Top             =   1200
      Width           =   1095
   End
   Begin VB.Label LabelRoipreset 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   86
      Top             =   3360
      Width           =   975
   End
   Begin VB.Label Label17 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Roipreset:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   85
      Top             =   3360
      Width           =   1095
   End
   Begin VB.Label LabelOffset 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   84
      Top             =   2400
      Width           =   975
   End
   Begin VB.Label Label16 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Offset:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   83
      Top             =   2400
      Width           =   1095
   End
   Begin VB.Label LabelBitshift 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   82
      Top             =   2880
      Width           =   975
   End
   Begin VB.Label Label14 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Bitshift:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   81
      Top             =   2880
      Width           =   1095
   End
   Begin VB.Label LabelXdim 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   80
      Top             =   2640
      Width           =   975
   End
   Begin VB.Label Label11 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Xdim:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   79
      Top             =   2640
      Width           =   1095
   End
   Begin VB.Label LabelParam 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   78
      Top             =   2160
      Width           =   975
   End
   Begin VB.Label Label9 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Param:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   77
      Top             =   2160
      Width           =   1095
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   13
      Left            =   2520
      TabIndex        =   76
      Top             =   6960
      Width           =   1935
   End
   Begin VB.Label Label39 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Filename:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   1560
      TabIndex        =   75
      Top             =   6960
      Width           =   855
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   12
      Left            =   2520
      TabIndex        =   74
      Top             =   6600
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   11
      Left            =   2520
      TabIndex        =   73
      Top             =   6360
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   10
      Left            =   2520
      TabIndex        =   72
      Top             =   6120
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   9
      Left            =   2520
      TabIndex        =   71
      Top             =   5880
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   8
      Left            =   2520
      TabIndex        =   70
      Top             =   5640
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   7
      Left            =   2520
      TabIndex        =   69
      Top             =   5400
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   6
      Left            =   2520
      TabIndex        =   68
      Top             =   5160
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   5
      Left            =   2520
      TabIndex        =   67
      Top             =   4920
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   4
      Left            =   2520
      TabIndex        =   66
      Top             =   4680
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   3
      Left            =   2520
      TabIndex        =   65
      Top             =   4440
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   2
      Left            =   2520
      TabIndex        =   64
      Top             =   4200
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   1
      Left            =   2520
      TabIndex        =   63
      Top             =   3960
      Width           =   1935
   End
   Begin VB.Label LabelLine 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   0
      Left            =   2520
      TabIndex        =   62
      Top             =   3720
      Width           =   1935
   End
   Begin VB.Label LabelRespons 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      BorderStyle     =   1  'Fixed Single
      ForeColor       =   &H80000008&
      Height          =   1935
      Left            =   240
      TabIndex        =   61
      Top             =   4440
      Width           =   1935
   End
   Begin VB.Label Label36 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Line0:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   1800
      TabIndex        =   60
      Top             =   3720
      Width           =   495
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   23
      Left            =   9360
      TabIndex        =   58
      Top             =   6000
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   22
      Left            =   9360
      TabIndex        =   57
      Top             =   5760
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   21
      Left            =   9360
      TabIndex        =   56
      Top             =   5520
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   20
      Left            =   9360
      TabIndex        =   55
      Top             =   5280
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   19
      Left            =   9360
      TabIndex        =   54
      Top             =   5040
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   18
      Left            =   9360
      TabIndex        =   53
      Top             =   4800
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   17
      Left            =   9360
      TabIndex        =   52
      Top             =   4560
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   16
      Left            =   9360
      TabIndex        =   51
      Top             =   4320
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   15
      Left            =   9360
      TabIndex        =   50
      Top             =   4080
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   14
      Left            =   9360
      TabIndex        =   49
      Top             =   3840
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   13
      Left            =   9360
      TabIndex        =   48
      Top             =   3600
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   12
      Left            =   9360
      TabIndex        =   47
      Top             =   3360
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   11
      Left            =   9360
      TabIndex        =   46
      Top             =   3120
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   10
      Left            =   9360
      TabIndex        =   45
      Top             =   2880
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   9
      Left            =   9360
      TabIndex        =   44
      Top             =   2640
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   8
      Left            =   9360
      TabIndex        =   41
      Top             =   2400
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   7
      Left            =   9360
      TabIndex        =   40
      Top             =   2160
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   6
      Left            =   9360
      TabIndex        =   39
      Top             =   1920
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   5
      Left            =   9360
      TabIndex        =   38
      Top             =   1680
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   4
      Left            =   9360
      TabIndex        =   37
      Top             =   1440
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   3
      Left            =   9360
      TabIndex        =   36
      Top             =   1200
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   2
      Left            =   9360
      TabIndex        =   35
      Top             =   960
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   1
      Left            =   9360
      TabIndex        =   34
      Top             =   720
      Width           =   975
   End
   Begin VB.Label LabelData 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Index           =   0
      Left            =   9360
      TabIndex        =   33
      Top             =   480
      Width           =   975
   End
   Begin VB.Label LabelCalpoints 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   32
      Top             =   1920
      Width           =   975
   End
   Begin VB.Label Label34 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Calpoints:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   31
      Top             =   1920
      Width           =   1095
   End
   Begin VB.Label LabelActive 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   30
      Top             =   3120
      Width           =   975
   End
   Begin VB.Label Label33 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Active:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   29
      Top             =   3120
      Width           =   1095
   End
   Begin VB.Label LabelCaluse 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   28
      Top             =   1680
      Width           =   975
   End
   Begin VB.Label Label31 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Caluse:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   27
      Top             =   1680
      Width           =   1095
   End
   Begin VB.Label LabelNregions 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   26
      Top             =   1440
      Width           =   975
   End
   Begin VB.Label Label30 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Nregions:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   25
      Top             =   1440
      Width           =   1095
   End
   Begin VB.Label LabelRoimin 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   24
      Top             =   960
      Width           =   975
   End
   Begin VB.Label Label15 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Roimin:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   23
      Top             =   960
      Width           =   1095
   End
   Begin VB.Label LabelCftfak 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   22
      Top             =   720
      Width           =   975
   End
   Begin VB.Label Label13 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Cftfak:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   21
      Top             =   720
      Width           =   1095
   End
   Begin VB.Label LabelRange 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   7560
      TabIndex        =   20
      Top             =   480
      Width           =   975
   End
   Begin VB.Label Label12 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Range:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   6360
      TabIndex        =   19
      Top             =   480
      Width           =   1095
   End
   Begin VB.Label Label10 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Spectra#"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   4680
      TabIndex        =   16
      Top             =   120
      Width           =   855
   End
   Begin VB.Label LabelStarts 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   2760
      TabIndex        =   14
      Top             =   1200
      Width           =   975
   End
   Begin VB.Label Label5 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Starts:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   1800
      TabIndex        =   13
      Top             =   1200
      Width           =   855
   End
   Begin VB.Label LabelStarted 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   2760
      TabIndex        =   12
      Top             =   480
      Width           =   975
   End
   Begin VB.Label Label4 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Started:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   1800
      TabIndex        =   11
      Top             =   480
      Width           =   855
   End
   Begin VB.Label LabelRuntime 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   2760
      TabIndex        =   6
      Top             =   720
      Width           =   975
   End
   Begin VB.Label Label3 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Runtime:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   1800
      TabIndex        =   5
      Top             =   720
      Width           =   855
   End
   Begin VB.Label LabelSweeps 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "0"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   2760
      TabIndex        =   4
      Top             =   960
      Width           =   975
   End
   Begin VB.Label Label2 
      Appearance      =   0  'Flat
      BackColor       =   &H80000005&
      Caption         =   "Sweeps:"
      ForeColor       =   &H80000008&
      Height          =   255
      Left            =   1800
      TabIndex        =   3
      Top             =   960
      Width           =   855
   End
End
Attribute VB_Name = "Form1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Dim Status As Acqstatus
Dim Setting As Acqsetting
Dim Dsetting As Datsetting
Dim OldStarted As Integer
Dim Mcano As Long
Dim Sysno As Long
Dim Chan As Long
Dim Hist(24) As Long
Dim Toggle As Integer


Private Sub CommandContinue_Click()
  Call Continue(0)
End Sub

Private Sub CommandDatasettings_Click()
  Call GetDatSetting(Dsetting)
  LabelSavedata.Caption = Dsetting.SaveData
  LabelAutoinc.Caption = Dsetting.Autoinc
  LabelFmt.Caption = Dsetting.Fmt
  LabelMpafmt.Caption = Dsetting.Mpafmt
  LabelSephead.Caption = Dsetting.Sephead
  LabelSmpts.Caption = Dsetting.Smpts
  LabelAddcal.Caption = Dsetting.Caluse
  LabelMpafilename.Caption = Dsetting.Filename
  Labelspecfile.Caption = Dsetting.Specfile
  LabelCommand.Caption = Dsetting.Command
End Sub

Private Sub CommandErase_Click()
  Call EraseData(0)
End Sub

Private Sub CommandExecute_Click()
  Dim a As String * 1024
  Mid$(a, 1) = TextCommand.Text
  Call RunCmd(0, a)
  LabelRespons.Caption = a
  Mcano = Val(TextMC.Text)
  Ret = GetStatus(Mcano)
  Ret = GetStatusData(Status, 0)
  Call UpdateMpStatus
  Ret = GetStatusData(Status, Mcano)
  Call UpdateStatus
End Sub

Private Sub CommandGetspec_Click()
  Mcano = Val(TextMC.Text)
  Chan = Val(TextChan.Text)
  Call GetBlock(Hist(0), Chan, Chan + 24, 1, Mcano)
  For I = 0 To 23 Step 1
    LabelData(I).Caption = Hist(I)
  Next I
End Sub

Private Sub CommandGetstring_Click()
  Dim b As String * 1024
  Mcano = Val(TextMC.Text)
  Ret = LVGetStr(b, Mcano)
  LabelLine(0).Caption = Mid$(b, 1, 60)
  LabelLine(1).Caption = Mid$(b, 61, 60)
  LabelLine(2).Caption = Mid$(b, 121, 60)
  LabelLine(3).Caption = Mid$(b, 181, 60)
  LabelLine(4).Caption = Mid$(b, 241, 60)
  LabelLine(5).Caption = Mid$(b, 301, 60)
  LabelLine(6).Caption = Mid$(b, 361, 60)
  LabelLine(7).Caption = Mid$(b, 421, 60)
  LabelLine(8).Caption = Mid$(b, 481, 60)
  LabelLine(9).Caption = Mid$(b, 541, 60)
  LabelLine(10).Caption = Mid$(b, 601, 60)
  LabelLine(11).Caption = Mid$(b, 881, 60)
  LabelLine(12).Caption = Mid$(b, 961, 60)
  LabelLine(13).Caption = Mid$(b, 661, 100)
End Sub

Private Sub CommandHalt_Click()
  Call Halt(0)
End Sub


Private Sub CommandSave_Click()
  Call SaveData(0, 1)
End Sub

Private Sub CommandSetting_Click()
  Mcano = Val(TextMC.Text)
  If GetSettingData(Setting, Mcano) = 1 Then
      Call UpdateSetting
  End If
End Sub

Private Sub CommandStart_Click()
  Call Start(0)
End Sub

Private Sub CommandUpdate_Click()
  Mcano = Val(TextMC.Text)
  Ret = GetStatus(Mcano)
  If GetStatusData(Status, Mcano) = 1 Then
      Call UpdateStatus
  End If
End Sub

Private Sub Form_Load()
  OldStarted = 0
  Mcano = 0
  Sysno = 0
  Chan = 0
  Ret = ServExec(0)
  Ret = GetStatus(0)
  Ret = GetStatusData(Status, 0)
  Call UpdateMpStatus
  Ret = GetStatusData(Status, Mcano)
  Call UpdateStatus
  Ret = GetSettingData(Setting, 0)
  Call UpdateSetting
End Sub




Private Sub Timer1_Timer()
  Mcano = Val(TextMC.Text)
  Ret = GetStatus(0)
  If GetStatusData(Status, 0) = 1 Then
    If Status.Val > 0 Or OldStarted > 0 Then
      Toggle = Not Toggle
      OldStarted = Status.Val
      Call UpdateMpStatus
      If GetStatusData(Status, Mcano) = 1 Then
        Call UpdateStatus
      End If
    End If
  End If
End Sub

Private Sub UpdateMpStatus()
      LabelStarted.Caption = Status.Val
      LabelRuntime.Caption = Status.Cnt(0)
      LabelSweeps.Caption = Status.Cnt(5)
      LabelStarts.Caption = Status.Cnt(6)
End Sub

Private Sub UpdateStatus()
      LabelMaxval.Caption = Status.Val1
      LabelOfls.Caption = Status.Cnt(1)
      LabelTotalsum.Caption = Status.Cnt(2)
      LabelRoisum.Caption = Status.Cnt(3)
      LabelTotalrate.Caption = Format$(Status.Cnt(4), "######0.0#")
End Sub

Private Sub UpdateSetting()
      LabelRange.Caption = Setting.Range
      LabelCftfak.Caption = Setting.Cftfak
      LabelRoimin.Caption = Setting.Roimin
      LabelRoimax.Caption = Setting.Roimax
      LabelNregions.Caption = Setting.Nregions
      LabelCaluse.Caption = Setting.Caluse
      LabelCalpoints.Caption = Setting.Calpoints
      LabelParam.Caption = Setting.Param
      LabelOffset.Caption = Setting.Offset
      LabelXdim.Caption = Setting.Xdim
      LabelBitshift.Caption = Setting.Bitshift
      LabelActive.Caption = Setting.Active
      LabelRoipreset.Caption = Setting.Roipreset
End Sub

