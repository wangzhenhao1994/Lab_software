#define  WINDOWSNT
#undef  WINDOWS95
#undef  WINDOWS31

#ifdef WINDOWS31

#define GET_WM_COMMAND_ID(w)  w
#define GET_WM_COMMAND_CMD(w,l) HIWORD(l)
#define GET_WM_COMMAND_HWND(l) LOWORD(l)
#define GET_WM_SCRHWND(l) HIWORD(l)
#define GET_WM_SCROLLPOS(w,l) LOWORD(l)
#define FIND_WINDOW(a,b) FindWindow(b,a)
#define HUGE huge
#define USHORT unsigned short
#define SetForegroundWindow(w)
#define APIENTRY FAR PASCAL
#define Sleep(t) waitmsec(t)

#else

#define GET_WM_COMMAND_ID(w)  LOWORD(w)
#define GET_WM_COMMAND_CMD(w,l) HIWORD(w)
#define GET_WM_COMMAND_HWND(l) l
#define GET_WM_SCRHWND(l) l
#define GET_WM_SCROLLPOS(w,l) (short)HIWORD(w)
#define FIND_WINDOW(a,b) FindWindow(a,b)
#define HUGE
#define _fmemcpy memcpy
#define _fstrcpy strcpy

#endif

typedef struct {
        int use;
        int port;
        unsigned long baud;
        int dbits;
        int sbits;
        int parity;
        int echo;
        HWND hwndserver;
        LPSTR cmd;
} COMCTL, far *LPCOMCTL;

#define ST_RUNTIME    0
#define ST_OFLS		  1
#define ST_TOTALSUM   2
#define ST_ROISUM     3
#define ST_ROIRATE    4
#define ST_SWEEPS     5
#define ST_STARTS     6

typedef struct{
  unsigned long started; // aquisition status 
  unsigned long maxval;  // maxval
  double cnt[8];        // status: runtime in msec, ofls, 
						// total sum, roi sum, roi rate, sweeps, starts
} ACQSTATUS;

typedef struct {
  long savedata;         // bit 0: auto save after stop
						 // bit 1: write listfile
						 // bit 2: listfile only, no evaluation
  long autoinc;          // 1 if auto increment filename
  long fmt;              // format type (seperate spectra): 
						 // 0 == ASCII, 1 == binary,
                         // 2 == CSV
  long mpafmt;           // format used in mpa datafiles 
  long sephead;          // seperate Header 
  long smpts;
  long caluse;
  char filename[256];
  char specfile[256];
  char command[256];
} DATSETTING;

typedef struct {
  long use;              // 1 if Replay Mode ON
  long modified;         // Bit 0: 1 if different settings are used
						 // (Bit 1: Write ASCII, reserved)
  long limit;            // 0: all, 
                        // 1: limited sweep range
  long speed;			// replay speed in units of 100 kB / sec
  double startsfrom;    // first start#
  double startsto;      // last start#
  double startspreset;  // last start - first start
  char filename[256];
} REPLAYSETTING;

typedef struct{
  long range;            // spectrum length
  long cftfak;           // LOWORD: 256 * cft factor (t_after_peak / t_to_peak)
						 // HIWORD: max pulse width for CFT 
  long roimin;           // lower ROI limit
  long roimax;           // upper limit: roimin <= channel < roimax
  long nregions;         // number of regions
  long caluse;           // bit0: 1 if calibration used, higher bits: formula
  long calpoints;        // number of calibration points
  long param;            // (reserved:) for MAP and POS: LOWORD=x, HIWORD=y 
  long offset;           // (reserved:) zoomed MAPS: LOWORD: xoffset, HIWORD, yoffset
  long xdim;			//  (reserved:) x resolution of maps
  unsigned long bitshift;  // LOWORD: Binwidth = 2 ^ (bitshift)
						   // HIWORD: Threshold for Coinc
  long active;      // Spectrum definition words for CHN1..6:
                           // active & 0xF  ==0 not used 
                           //               ==1 single
						// bit 8: Enable Tag bits
						// bit 9: start with rising edge 
						// bit 10: time under threshold for pulse width
						// bit 11: pulse width mode for any spectra with both edges enabled
					// Spectrum definition words for calc. spectra:
                           // active & 0xF  ==3 MAP, ((x-xoffs)>>xsh) x ((y-yoffs)>>ysh)
                           //                 ((x-xoffs)>>xsh) x ((y-timeoffs)>>timesh)  
                           //              or ((x-timeoffs)>>timesh x ((y-yoffs)>>ysh)  
						   //         bit4=1: x zoomed MAP
						   //         bit5=1: y zoomed MAP
						   //               ==5 SUM, (x + y)>>xsh
						   //               ==6 DIFF,(x - y + range)>>xsh
  						   //               ==7 ANY, (for compare)
						   //               ==8 COPY, x
						   //               ==9 DLL  fDLL(x,y,z), 
                           //               ==0xA Sweep HISTORY, Sweepnum(x)
// bit 8..11 xsh, bit 12..15 ysh or bit 8..15 xsh
						   // HIWORD(active) = condition no. (0=no condition)
  double eventpreset;   // ROI preset value
  double dummy1;        // (for future use..)
  double dummy2;		// 
  double dummy3;		// 
} ACQSETTING;

typedef struct{
  long range;            // spectrum length
  long cftfak;           // LOWORD: 256 * cft factor (t_after_peak / t_to_peak)
						 // HIWORD: max pulse width for CFT 
  long roimin;           // lower ROI limit
  long roimax;           // upper limit: roimin <= channel < roimax
  long nregions;         // number of regions
  long caluse;           // bit0: 1 if calibration used, higher bits: formula
  long calpoints;        // number of calibration points
  long param;            // (reserved:) for MAP and POS: LOWORD=x, HIWORD=y 
  long offset;           // (reserved:) zoomed MAPS: LOWORD: xoffset, HIWORD, yoffset
  long xdim;			//  (reserved:) x resolution of maps
  unsigned long bitshift;  // LOWORD: Binwidth = 2 ^ (bitshift)
						   // HIWORD: Threshold for Coinc
  long active;      // Spectrum definition words for CHN1..6:
                           // active & 0xF  ==0 not used 
                           //               ==1 enabled
						// bit 8: Enable Tag bits
						// bit 9: start with rising edge 
						// bit 10: time under threshold for pulse width
						// bit 11: pulse width mode for any spectra with both edges enabled
					// Spectrum definition words for calc. spectra:
                           // active & 0xF  ==3 MAP, ((x-xoffs)>>xsh) x ((y-yoffs)>>ysh)
  						   //         bit4=1: x zoomed MAP
						   //         bit5=1: y zoomed MAP
						   //               ==5 SUM, (x + y)>>xsh
						   //               ==6 DIFF,(x - y + range)>>xsh
  						   //               ==7 ANY, (for compare)
						   //               ==8 COPY, x
						   //               ==10 SW-HIS, Sweep History 
                           // bit 8..11 xsh, bit 12..15 ysh or bit 8..15 xsh
						   // HIWORD(active) = condition no. (0=no condition)
  double eventpreset;   // ROI preset value
  double dummy1;        // (for future use..)
  double dummy2;		// 
  double dummy3;        // 
						// MPANT or Server private saved settings:
  long type;			// 0=single, 1=MAP, 2=ISO...
  long ydim;			// y resolution of maps
  long reserved[16];
} EXTACQSETTING;

typedef struct {
  long sweepmode;       // sweepmode & 0xF: 0 = normal, 
						// 1=differential (relative to first stop in sweep)
						// 4=sequential
						// 5=seq.+diff (Ch1), bit0 = differential mode
						// 6 = CORRELATIONS
						// 7 = diff.+Corr.
						// 9=differential to stop in Ch2, bit3 = Ch2 ref (diff.mode)
						// 0xD = seq.+diff (Ch2)
						// 0xF = Corr.+diff (Ch2)
						// bit 4: Softw. Start
						// bit 6: Endless
						// bit 7: Start event generation
						// bit 8: Enable Tag bits
						// bit 9: start with rising edge 
						// bit 10: time under threshold for pulse width
						// bit 11: pulse width mode for any spectra with both edges enabled
						// bit 12: abandon Sweepcounter in Data
						// bit 13: "one-hot" mode with tagbits
						// bit 14: ch6 ref (diff.mode)
						// bit 15: enable ch6 input
                        // bit 16..bit 20 ~(input channel enable) 
						// bit 24: require data lost bit in data
						// bit 25: don't allow 6 byte datalength
  long prena;           // bit 0: realtime preset enabled
						// bit 1: 
                        // bit 2: sweep preset enabled
                        // bit 3: ROI preset enabled
						// bit 4: Starts preset enabled
                        // bit 5: ROI2 preset enabled
                        // bit 6: ROI3 preset enabled
                        // bit 7: ROI4 preset enabled
                        // bit 8: ROI5 preset enabled
                        // bit 9: ROI6 preset enabled
  long cycles;          // for sequential mode
  long sequences;       // 
  long syncout;         // LOWORD: sync out; bit 0..5 NIM syncout, bit 8..13 TTL syncout
						// bit7: NIM syncout_invert, bit15: TTL syncout_invert
						// 0="0", 1=10 MHz, 2=78.125 MHz, 3=100 MHz, 4=156.25 MHz,
						// 5=200 MHz, 6=312.5 MHz, 7=Ch0, 8=Ch1, 9=Ch2, 10=Ch3,
						// 11=Ch4, 12=Ch5, 13=GO, 14=Start_of_sweep, 15=Armed,
						// 16=SYS_ON, 17=WINDOW, 18=HOLD_OFF, 19=EOS_DEADTIME
						// 20=TIME[0],...,51=TIME[31], 52...63=SWEEP[0]..SWEEP[11]
                        //
  long digio;           // LOWORD: Use of Dig I/O, GO Line:
                        // bit 0: status dig 0..3
                        // bit 1: Output digval and increment digval after stop
                        // bit 2: Invert polarity
						// (bit 3: Push-Pull output, not possible)
                        // bit 4..7:  Input pins 4..7 Trigger System 1..4
						// bit 8: GOWATCH
						// bit 9: GO High at Start
						// bit 10: GO Low at Stop
						// bit 11: Clear at triggered start
						// bit 12: Only triggered start
  long digval;			// digval=0..255 value for samplechanger
  long dac0;           //  DAC0 value (START) 
					   //  bit 16: Start with rising edge
  long dac1;           //  DAC1 value (STOP 1) 
  long dac2;           //  DAC2 value (STOP 2)
  long dac3;           //  DAC3 value (STOP 3)
  long dac4;           //  DAC4 value (STOP 4)
  long dac5;           //  DAC5 value (STOP 5)
						// bit (14,15) of each word: 0=falling, 1=rising, 2=both, 3=both+CFT 
						// bit 17 of each: pulse width mode under threshold
  int fdac;				// Feature DAC 0..16383 --> 0..2.5V 
  int tagbits;          // number of tagbits
  int extclk;			// use external clock
  long maxchan;			// number of input channels (=6)
  long serno;			// serial number
  long ddruse;          // bit0: DDR_USE, bit1: DDR_2GB
						// bits[2:3]: usb_usage
						// bits[4:5]: wdlen
  long active;          // module in system
  double holdafter;	    // Hold off
  double swpreset;      // sweep preset value
  double fstchan;		// acquisition delay
  double timepreset;    // time preset
} BOARDSETTING;

typedef struct {
  int nDevices;          // Number of channels = number of modules * 6
  int nDisplays;         // Number of histograms = nDevices + Positions + Maps
  int nSystems;          // Number of independent systems = 1
  int bRemote;           // 1 if server controlled by MPANT
  unsigned int sys;      // System definition word:
                           // bit0=0, bit1=0: dev#0 in system 1
                           // bit0=1, bit1=0: dev#0 in system 2
                           // bit0=0, bit1=1: dev#0 in system 3
                           // bit0=1, bit1=1: dev#0 in system 4
                           // bit2..bit6: 
                           // bit6=1, bit7=1: dev#3 in system 4 
  int sys0[56];           // (reserved:) System definition words for CHN1..18:
                           // bit 0 CHN active
                           // bit 1 =1 CHN coinc, =0 single
                           // bit 2..4 CHN in system1..7
  int sys1[56];           // (reserved:) CHN in System
} ACQDEF;

typedef struct{
  unsigned long HUGE *s0;          // pointer to spectrum
  unsigned long *region;       // pointer to regions
  unsigned char *comment0;     // pointer to strings
  double *cnt;                 // pointer to counters
  HANDLE hs0;
  HANDLE hrg;
  HANDLE hcm;
  HANDLE hct;
} ACQDATA;


