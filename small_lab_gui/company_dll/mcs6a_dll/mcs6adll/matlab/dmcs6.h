#ifdef __cplusplus
extern "C"	
{
#endif

#include "struct.h"
#define MAXCNT              448
#define MAXDSP				64
#define MAXDEV              3


#define ID_SAVE             103
#define ID_CONTINUE         106
#define ID_START            109
#define ID_BREAK            137
#define ID_NEWSETTING       139
#define ID_GETSTATUS        141
#define ID_SAVEFILE         151
#define ID_ERASE            154
#define ID_LOADFILE         155
#define ID_NEWDATA          160
#define ID_HARDWDLG         161
#define ID_SAVEFILE2                194
#define ID_LOADFILE2                203
#define ID_SAVEFILE3                217
#define ID_LOADFILE3                219
#define ID_SAVEFILE4                223
#define ID_LOADFILE4                225
#define ID_LOADFILE5                226
#define ID_LOADFILE6                227
#define ID_LOADFILE7                228
#define ID_LOADFILE8                229
#define ID_SAVEFILE5                230
#define ID_SAVEFILE6                231
#define ID_SAVEFILE7                232
#define ID_SAVEFILE8                233
#define ID_SUMFILE                      234
#define ID_SUMFILE2                     235
#define ID_SUMFILE3                     236
#define ID_SUMFILE4                     237
#define ID_SUMFILE5                     238
#define ID_SUMFILE6                     239
#define ID_SUMFILE7                     240
#define ID_SUMFILE8                     241
#define ID_LEDBLINK0                    280
#define ID_LEDBLINK1                    281
#define ID_LEDBLINK2                    282
#define ID_SUBTRACT                     289
#define ID_SMOOTH                       290
#define ID_SUBTRACT2                    296
#define ID_SMOOTH2                      297
#define ID_SUBTRACT3                    298
#define ID_SMOOTH3                      299
#define ID_SUBTRACT4                    300
#define ID_SMOOTH4                      301
#define ID_SUBTRACT5                    302
#define ID_SMOOTH5                      303
#define ID_SUBTRACT6                    304
#define ID_SMOOTH6                      305
#define ID_SUBTRACT7                    306
#define ID_SMOOTH7                      307
#define ID_SUBTRACT8                    308
#define ID_SMOOTH8                      309
#define ID_SAVEFILE9                 310
#define ID_SAVEFILE10                311
#define ID_SAVEFILE11                312
#define ID_SAVEFILE12                313
#define ID_SAVEFILE13                314
#define ID_SAVEFILE14                315
#define ID_SAVEFILE15                316
#define ID_SAVEFILE16                317
#define ID_LOADFILE9                 318
#define ID_LOADFILE10                319
#define ID_LOADFILE11                320
#define ID_LOADFILE12                321
#define ID_LOADFILE13                322
#define ID_LOADFILE14                323
#define ID_LOADFILE15                324
#define ID_LOADFILE16                325
#define ID_SUMFILE9                  326
#define ID_SUMFILE10                 327
#define ID_SUMFILE11                 328
#define ID_SUMFILE12                 329
#define ID_SUMFILE13                 330
#define ID_SUMFILE14                 331
#define ID_SUMFILE15                 332
#define ID_SUMFILE16                 333
#define ID_SUBTRACT9                 334
#define ID_SUBTRACT10                335
#define ID_SUBTRACT11                336
#define ID_SUBTRACT12                337
#define ID_SUBTRACT13                338
#define ID_SUBTRACT14                339
#define ID_SUBTRACT15                340
#define ID_SUBTRACT16                341
#define ID_COMBDLG          401
#define ID_DATADLG          402
#define ID_MAPLSTDLG        403
#define ID_REPLDLG          404
#define ID_ERASE3          1109
#define ID_ERASE4          1110
#define ID_ERASEFILE2      1111
#define ID_ERASEFILE3      1112
#define ID_ERASEFILE4      1113
#define ID_START2          1114
#define ID_BREAK2          1115
#define ID_CONTINUE2       1116
#define ID_START3          1117
#define ID_BREAK3          1118
#define ID_CONTINUE3       1119
#define ID_START4          1120
#define ID_BREAK4          1121
#define ID_CONTINUE4       1122
#define ID_RUNCMD                       1123
#define ID_RUNCMD2                      1124
#define ID_RUNCMD3                      1125
#define ID_RUNCMD4                      1126
#define ID_RUNCMD5                      1127
#define ID_RUNCMD6                      1128
#define ID_RUNCMD7                      1129
#define ID_RUNCMD8                      1130
#define ID_ERASEFILE5                   1131
#define ID_ERASEFILE6                   1132
#define ID_ERASEFILE7                   1133
#define ID_ERASEFILE8                   1134
#define ID_DIGINOUT			1137
#define ID_ERASE2          1164

/*** FUNCTION PROTOTYPES (do not change) ***/

#ifdef DLL
BOOL APIENTRY DllMain(HANDLE hInst, DWORD ul_reason_being_called, LPVOID lpReserved);

VOID APIENTRY StoreSettingData(ACQSETTING FAR *Setting, int nDisplay);
                                           // Stores Settings into the DLL
int APIENTRY GetSettingData(ACQSETTING FAR *Setting, int nDisplay);
                                           // Get Settings stored in the DLL
VOID APIENTRY StoreExtSettingData(EXTACQSETTING FAR *Setting, int nDisplay);
                                      // Stores extended Settings into the DLL
int APIENTRY GetExtSettingData(EXTACQSETTING FAR *Setting, int nDisplay);
                                      // Get extended Settings stored in the DLL
VOID APIENTRY StoreStatusData(ACQSTATUS FAR *Status, int nDisplay);
                                           // Store the Status into the DLL
int APIENTRY GetStatusData(ACQSTATUS FAR *Status, int nDisplay);
                                           // Get the Status
VOID APIENTRY Start(int nSystem);        // Start
VOID APIENTRY Halt(int nSystem);         // Halt
VOID APIENTRY Continue(int nSystem);     // Continue
VOID APIENTRY NewSetting(int nDevice);   // Indicate new Settings to Server
UINT APIENTRY ServExec(HWND ClientWnd);  // Execute the Server 
VOID APIENTRY StoreData(ACQDATA FAR *Data, int nDisplay);
                                           // Stores Data pointers into the DLL
int APIENTRY GetData(ACQDATA FAR *Data, int nDisplay);
                                           // Get Data pointers
long APIENTRY GetSpec(long i, int nDisplay);
                                           // Get a spectrum value
VOID APIENTRY SaveSetting(void);         // Save Settings
int APIENTRY GetStatus(int nDevice);     // Request actual Status from Server
VOID APIENTRY Erase(int nSystem);        // Erase spectrum
VOID APIENTRY SaveData(int nDisplay, int all);     // Saves data
VOID APIENTRY GetBlock(long FAR *hist, int start, int end, int step,
  int nDisplay);                           // Get a block of spectrum data
VOID APIENTRY StoreDefData(ACQDEF FAR *Def);
                                           // Store System Definition into DLL
int APIENTRY GetDefData(ACQDEF FAR *Def);
                                           // Get System Definition
VOID APIENTRY LoadData(int nDisplay, int all);     // Loads data
VOID APIENTRY AddData(int nDisplay, int all);      // Adds data
VOID APIENTRY SubData(int nDisplay, int all);      // Subtracts data
VOID APIENTRY Smooth(int nDisplay);       // Smooth data
VOID APIENTRY NewData(void);             // Indicate new ROI or string Data
VOID APIENTRY HardwareDlg(int item);     // Calls the Settings dialog box
VOID APIENTRY UnregisterClient(void);    // Clears remote mode from MCDWIN
VOID APIENTRY DestroyClient(void);       // Close MCDWIN
UINT APIENTRY ClientExec(HWND ServerWnd);
                                           // Execute the Client MCDWIN.EXE
int APIENTRY LVGetDat(unsigned long HUGE *datp, int nDisplay);
                                           // Copies the spectrum to an array
VOID APIENTRY RunCmd(int nDisplay, LPSTR Cmd);
                                           // Executes command
int APIENTRY LVGetRoi(unsigned long FAR *roip, int nDisplay);
                                     // Copies the ROI boundaries to an array
int APIENTRY LVGetOneRoi(int nDisplay, int roinum, long *x1, long *x2);
									 // Get one ROI boundary
int APIENTRY LVGetCnt(double far *cntp, int nDisplay);
                                           // Copies Cnt numbers to an array
int APIENTRY LVGetStr(char far *strp, int nDisplay);
                                           // Copies strings to an array
VOID APIENTRY StoreMCSSetting(BOARDSETTING *Defmc, int ndev);
                                    // Store BOARDSETTING Definition into DLL
int APIENTRY GetMCSSetting(BOARDSETTING *Defmc, int ndev);
                                    // Get BOARDSETTING Definition from DLL
VOID APIENTRY StoreDatSetting(DATSETTING *Defdat);
                                    // Store Data Format Definition into DLL
int APIENTRY GetDatSetting(DATSETTING *Defdat);
                                    // Get Data Format Definition from DLL
VOID APIENTRY StoreReplaySetting(REPLAYSETTING *Repldat);
                                    // Store Replay Settings into DLL
int APIENTRY GetReplaySetting(REPLAYSETTING *Repldat);
                                    // Get Replay Settings from DLL
int APIENTRY GetDatInfo(int nDisplay, long *xmax, long *ymax);
                                    // returns spectra length;
int APIENTRY GetDatPtr(int nDisplay, long *xmax, long *ymax, unsigned long * *pt);
                                    // Get a temporary pointer to spectra data
int APIENTRY ReleaseDatPtr(void);
									// Release temporary data pointer
long APIENTRY GetSVal(int DspID, long xval);
			// Get special display data like projections or slices from MPANT 
int APIENTRY BytearrayToShortarray(short *Shortarray, char *Bytearray, int length);
		    // auxiliary function for VB.NET to convert strings
int APIENTRY LedBlink(int nDev);
			// Lets the front leds blink for a while
int APIENTRY DigInOut(int value, int enable);  // controls Dig I/0 ,
								  // returns digin
#else
typedef int (WINAPI *IMPAGETSETTING) (ACQSETTING FAR *Setting, int nDisplay);
                                           // Get Spectra Settings stored in the DLL                                          
typedef int (WINAPI *IMPAGETSTATUS) (ACQSTATUS FAR *Status, int nDisplay);
                                           // Get the Status
typedef VOID (WINAPI *IMPARUNCMD) (int nDisplay, LPSTR Cmd);
                                           // Executes command
typedef int (WINAPI *IMPAGETCNT) (double FAR *cntp, int nDisplay);
                                           // Copies Cnt numbers to an array
typedef int (WINAPI *IMPAGETROI) (unsigned long FAR *roip, int nDisplay);
                                           // Copies the ROI boundaries to an array
typedef int (WINAPI *IMPAGETDEF) (ACQDEF FAR *Def);
                                           // Get System Definition
typedef int (WINAPI *IMPAGETDAT) (unsigned long HUGE *datp, int nDisplay);
                                           // Copies the spectrum to an array
typedef int (WINAPI *IMPAGETSTR) (char FAR *strp, int nDisplay);
                                           // Copies strings to an array
typedef UINT (WINAPI *IMPASERVEXEC) (HWND ClientWnd);  // Register client at server MCS6.EXE

typedef int (WINAPI *IMPANEWSTATUS) (int nDev);     // Request actual Status from Server

typedef int (WINAPI *IMPAGETMCSSET) (BOARDSETTING *Board, int nDevice);
                                    // Get MCSSettings from DLL
typedef int (WINAPI *IMPAGETDATSET) (DATSETTING *Defdat);
                                    // Get Data Format Definition from DLL
typedef int (WINAPI *IMPADIGINOUT) (int value, int enable);  // controls Dig I/0 ,
								  // returns digin
typedef int (WINAPI *IMPADACOUT) (int value);   // output Dac value as analogue voltage
typedef VOID (WINAPI *IMPASTART) (int nSystem);        // Start
typedef VOID (WINAPI *IMPAHALT) (int nSystem);         // Halt
typedef VOID (WINAPI *IMPACONTINUE) (int nSystem);     // Continue
typedef VOID (WINAPI *IMPAERASE) (int nSystem);        // Erase spectrum
#endif

#ifdef __cplusplus
}
#endif

