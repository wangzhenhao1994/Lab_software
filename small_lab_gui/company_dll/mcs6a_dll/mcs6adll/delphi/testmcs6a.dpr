program Testmcs6a;
{$APPTYPE CONSOLE}
{$X+}
uses
  Windows, sysutils;

const   ST_RUNTIME   =  0;
        ST_OFLS      =  1;
        ST_TOTALSUM  =  2;
        ST_ROISUM    =  3;
        ST_ROIRATE   =  4;
        ST_SWEEPS    =  5;
        ST_STARTS    =  6;

type    SmallIntPointer = ^SmallInt;


{Diese Typdefinitionen wurden vom File struct.h übernommen und in Delphi
 übersetzt}
   AcqStatusTyp = RECORD           //Status information
                started   : Cardinal;	// acquisition status, 0==OFF, 1==ON,
                                        // 3==READ OUT
                maxval    : Cardinal;   //
  		cnt       : array [0..7] of Double; // status: runtime in msec,
                                        // ofls, total sum,
                                        // roi sum, roi rate, sweeps, starts
                End;
   AcqStatusTypPointer = ^AcqStatusTyp;

   DatSettingTyp = RECORD               // Data settings
                savedata    : Cardinal; // bit 0: auto save after stop
                                        // bit 1: write list file
                                        // bit 2: list file only, no evaluation
                autoinc     : Cardinal; // 1 if auto increment filename
                fmt         : Cardinal; // format type: 0 == ASCII, 1 == binary,
                                        // 2 == CSV
                mpafmt      : Cardinal; // format used in mpa datafiles
                sephead     : Cardinal; // seperate Header
                smpts       : Cardinal; // number of points for smoothing operation
                caluse      : Cardinal; // 1 for using calibration for shifted spectra summing
                filename    : array [0..255] of Char; // mpa data filename
                specfile    : array [0..255] of Char; // seperate spectra filename
                command     : array [0..255] of Char; // command
                End;

   ReplaySettingTyp = RECORD            // Replay settings
                use         : Cardinal; // 1 if Replay Mode ON
                modified    : Cardinal; // 1 if different settings are used
                limit       : Cardinal; // 0: all, 1: limited time range
                speed       : Cardinal; // replay speed in units of 100 kB / sec
                startsfrom  : Double;   // first start no.
                startsto    : Double;   // last start no.
                startspreset : Double;  // last start - first
                filename    : array [0..255] of Char;
                End;

   AcqSettingTyp = RECORD		  // ADC or spectra Settings
  		range       : Cardinal;   // spectrum length, ADC range
  		cftfak      : Cardinal;   // LOWORD: 256 * cft factor (t_after_peak / t_to_peak)
                                          // HIWORD: max pulse width for CFT
   		roimin	    : Cardinal;   // lower ROI limit
  		roimax      : Cardinal;   // upper limit: roimin <= channel < roimax
  		nregions    : Cardinal; // number of regions
  		caluse      : Cardinal; // bit 0 == 1 if calibration used, higher bits: formula
  		calpoints   : Cardinal; // number of calibration points
  		param       : Cardinal; // for MAP and POS: LOWORD=x, HIGHWORD=y (rtime=256, RTC=257)
                offset      : Cardinal; // zoomed MAPS: LOWORD: xoffset, HIGHWORD: yoffset
  		xdim	    : Cardinal; // x resolution of maps
                bitshift    : Cardinal; // LOWORD: Binwidth = 2 ^ (bitshift)
			                // HIWORD: Threshold for Coinc
  		active      : Cardinal; // Spectrum definition words for CHN1..6:
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
  		roipreset   : Double;   // ROI preset value
  		dummy1      : Double;   // (for future use..)
  		dummy2      : Double;   //
                dummy3      : Double;   //
                End;
   AcqSettingTypPointer = ^AcqSettingTyp;

   ExtAcqSettingTyp = RECORD		// Settings
   		range       : Cardinal;   // spectrum length, ADC range
  		cftfak      : Cardinal;   // LOWORD: 256 * cft factor (t_after_peak / t_to_peak)
                                          // HIWORD: max pulse width for CFT
   		roimin	    : Cardinal;   // lower ROI limit
  		roimax      : Cardinal;   // upper limit: roimin <= channel < roimax
  		nregions    : Cardinal; // number of regions
  		caluse      : Cardinal; // bit 0 == 1 if calibration used, higher bits: formula
  		calpoints   : Cardinal; // number of calibration points
  		param       : Cardinal; // for MAP and POS: LOWORD=x, HIGHWORD=y (rtime=256, RTC=257)
                offset      : Cardinal; // zoomed MAPS: LOWORD: xoffset, HIGHWORD: yoffset
  		xdim	    : Cardinal; // x resolution of maps
                bitshift    : Cardinal; // LOWORD: Binwidth = 2 ^ (bitshift)
			                // HIWORD: Threshold for Coinc
  		active      : Cardinal; // Spectrum definition words for CHN1..6:
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
  		roipreset   : Double;   // ROI preset value
  		dummy1      : Double;   // (for future use..)
  		dummy2      : Double;   //
                dummy3      : Double;   //
		vtype       : Cardinal; // 0=single, 1=MAP, 2=ISO...
                ydim        : Cardinal; // y resolution of maps
		reserved    : array [0..12] of LongInt;
                End;
   ExtAcqSettingTypPointer = ^ExtAcqSettingTyp;

   AcqDataTyp = RECORD
    		s0          : Array of LongInt; // pointer to spectrum
  		region	    : Array of Cardinal; // pointer to regions
  		comment0    : Array of Char;     // pointer to strings
  		cnt	    : Array of Double;   // pointer to counters
  		hs0	    : Integer;
  		hrg	    : Integer;
  		hcm	    : Integer;
  		hct	    : Integer;
		End;

   AcqMCSTyp = RECORD
                sweepmode   : Cardinal;       // sweepmode & 0xF: 0 = normal,
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
                prena       : Cardinal;
                        // bit 0: realtime preset enabled
					// bit 1: reserved
                        // bit 2: sweep preset enabled
                        // bit 3: ROI preset enabled
                        // bit 4: Starts preset enabled
                        // bit 5: ROI2 preset enabled
                        // bit 6: ROI3 preset enabled
                        // bit 7: ROI4 preset enabled
                        // bit 8: ROI5 preset enabled
                        // bit 9: ROI6 preset enabled
                cycles      : Cardinal;       // for sequential mode
                sequences   : Cardinal;       //
                syncout     : Cardinal;
                            // LOWORD: sync out; bit 0..5 NIM syncout, bit 8..13 TTL syncout
		 	    // bit7: NIM syncout_invert, bit15: TTL syncout_invert
			    // 0="0", 1=10 MHz, 2=78.125 MHz, 3=100 MHz, 4=156.25 MHz,
			    // 5=200 MHz, 6=312.5 MHz, 7=Ch0, 8=Ch1, 9=Ch2, 10=Ch3,
			    // 11=Ch4, 12=Ch5, 13=GO, 14=Start_of_sweep, 15=Armed,
			    // 16=SYS_ON, 17=WINDOW, 18=HOLD_OFF, 19=EOS_DEADTIME
			    // 20=TIME[0],...,51=TIME[31], 52...63=SWEEP[0]..SWEEP[11]
                digio       : Cardinal;       // LOWORD: Use of Dig I/O, GO Line:
                        // bit 0: status dig 0..3
                        // bit 1: Output digval and increment digval after stop
                        // bit 2: Invert polarity
                        //  (bit 3: reserved)
                        // bit 4..7:  Input pins 4..7 Trigger System 1..4
                        // bit 8: GOWATCH
			// bit 9: GO High at Start
			// bit 10: GO Low at Stop
			// bit 11: Clear at triggered start
			// bit 12: Only triggered start
                digval      : Cardinal;       // digval=0..255 value for samplechanger
                dac0        : Cardinal;       // DAC0 value (START)
				//  bit 16: Start with rising edge
                dac1        : Cardinal;       // DAC1 value (STOP 1)
                dac2        : Cardinal;       // DAC2 value (STOP 2)
                dac3        : Cardinal;       // DAC3 value (STOP 3)
                dac4        : Cardinal;       // DAC4 value (STOP 4)
                dac5        : Cardinal;       // DAC5 value (STOP 5)
			// bit (14,15) of each DAC: 0=falling, 1=rising, 2=both, 3=both+CFT
			// bit 17 of each: pulse width mode under threshold
                fdac        : Cardinal;       // Feature DAC 0..16383 --> 0..2.5V
                tagbits     : Cardinal;       // Number of tagbits
                extclk      : Cardinal;       // use external clock
                maxchan     : Cardinal;       // number of input channels (=6)
                serno       : Cardinal;       // serial number
                ddruse      : Cardinal;       // bit0: DDR_USE, bit1: DDR_2GB
					      // bits[2:3]: usb_usage
					      // bits[4:5]: wdlen
                active      : Cardinal;       // module in system
                holdafter   : Double;         // Hold off
                swpreset    : Double;         // Sweep Preset
                fstchan     : Double;         // Acquisition delay
                timepreset  : Double;         // Realtime Preset
                End;


   AcqDefTyp = RECORD
  		nDevices    : Cardinal;    // Number of connected ADC Interfaces = max. 16
  		nDisplays   : Cardinal;    // Number of histograms = nDevices + Positions + Maps
  		nSystems    : Cardinal;    // Number of independent systems = 1
      		bRemote	    : Cardinal;    // 1 if server controlled by MPANT
  		sys	    : Cardinal;     // System definition word
                           // bit0=0, bit1=0: dev#0 in system 1
                           // bit0=1, bit1=0: dev#0 in system 2
                           // bit0=0, bit1=1: dev#0 in system 3
                           // bit0=1, bit1=1: dev#0 in system 4
                           // bit2..bit6: 
                           // bit6=1, bit7=1: dev#3 in system 4
                sys0        : array [0..55] of Cardinal;
                                // System definition words for CHN1..18:
                                // see active definition in ACQSETTING
                sys1        : array [0..55] of Cardinal;
                                // CHN in System (always 1)
                End;
   AcqDefTypPointer = ^AcqDefTyp;


   LpGet = function (var Setting : AcqSettingTyp;  // Get Settings stored in the DLL
                     nDisplay : Cardinal) : LongInt; stdcall;

   LpStat = function (var Status  : AcqSTatusTyp;   // Get Status stored in the DLL
                     nDisplay : Cardinal) : LongInt; stdcall;

   LpRun  = procedure (nDisplay : LongInt;      // Executes command
		     Cmd	  : PChar) ; stdcall;

   LpCnt  = function (var cntp    : Double;       // Copies Cnt numbers to an array
                     nDisplay : Cardinal) : LongInt; stdcall;

   LpRoi  = function (var roip    : Cardinal;     // Copies the ROI boundaries to an array
                     nDisplay : Cardinal) : LongInt; stdcall;

   LpDat  = function (var datp    : LongInt;      // Copies the spectrum to an array
                     nDisplay : Cardinal) : LongInt; stdcall;

   LpStr  = function (var strp    : Char;         // Copies strings to an array
                    nDisplay : Cardinal) : LongInt; stdcall;

   LpServ = function (ClientWnd : Cardinal) : Cardinal; stdcall;  // Register Client MCDWIN.EXE

   LpNewStat = function (nDevice : Cardinal) : LongInt; stdcall;  // Request actual Status from Server

   LpGetMCS = function (var Defmp3 : AcqMCSTyp;         // Get MCS Settings from DLL
                        nDevice : Cardinal) : LongInt; stdcall;

   LpGetDatSet = function (var Defdat : DatSettingTyp) : LongInt; stdcall;
                                        // Get Data Format Definition from DLL


var  Handle 	: Integer;
     TGet 	: LpGet;
     TStat 	: LpStat;
     TRun	: LpRun;
     TCnt	: LpCnt;
     TRoi       : LpRoi;
     TDat       : LpDat;
     TStr       : LpStr;
     TServ      : LpServ;
     TNewStat   : LpNewStat;
     TMcs       : LpGetMCS;
     TDatset    : LpGetDatSet;
     Setting    : AcqSettingTyp;
     MCSset     : AcqMCSTyp;
     {Data	: AcqDataTyp;
     Def        : AcqDefTyp;}
     Status     : AcqStatusTyp;
     Adc        : Cardinal;
     cmd        : String;
     Err        : LongInt;
     Spec       : Array[0..8191] of LongInt;

procedure PrintMpaStatus(var stat: AcqStatusTyp);
begin
  with stat do
  begin
    if started = 1 then
      writeln('ON')
    else if started = 3 then
      writeln('READ OUT')
    else
      writeln('OFF');
    writeln('runtime=  ', cnt[ST_RUNTIME]);
    writeln('sweeps=   ', cnt[ST_SWEEPS]);
    writeln('starts=   ', cnt[ST_STARTS]);
  end;
end;

procedure PrintStatus(var stat: AcqStatusTyp);
begin
  with stat do
  begin
    writeln('totalsum=  ', cnt[ST_TOTALSUM]);
    writeln('roisum=    ', cnt[ST_ROISUM]);
    writeln('rate=      ', cnt[ST_ROIRATE]);
    writeln('ofls=      ', cnt[ST_OFLS]);
  end;
end;

procedure PrintDatSetting(var datsett: DatSettingTyp);
begin
  with datsett do
  begin
    writeln('savedata= ', savedata);
    writeln('autoinc=  ', autoinc);
    writeln('fmt=      ', fmt);
    writeln('mpafmt=   ', mpafmt);
    writeln('sephead=  ', sephead);
    writeln('filename= ', String(filename));
  end;
end;

procedure PrintMCSSetting(var mpsett: AcqMCSTyp);
begin
  with mpsett do
  begin
    writeln('sweepmode=  ', sweepmode);
    writeln('prena=      ', prena);
    writeln('cycles=     ', cycles);
    writeln('sequences=  ', sequences);
    writeln('syncout=    ', syncout);
    writeln('digio=      ', digio);
    writeln('digval=     ', digval);
    writeln('dac0=       ', dac0);
    writeln('dac1=       ', dac1);
    writeln('dac2=       ', dac2);
    writeln('dac3=       ', dac3);
    writeln('dac4=       ', dac4);
    writeln('dac5=       ', dac5);
    writeln('fdac=       ', fdac);
    writeln('tagbits=    ', tagbits);
    writeln('extclk=     ', extclk);
    writeln('maxchan=    ', maxchan);
    writeln('serno=      ', serno);
    writeln('ddruse=     ', ddruse);
    writeln('active=     ', active);
    writeln('holdafter=  ', holdafter);
    writeln('swpreset=   ', swpreset);
    writeln('fstchan=    ', fstchan);
    writeln('timepreset= ', timepreset);
  end;
end;

procedure PrintSetting(var sett: AcqSettingTyp);
begin
  with sett do
  begin
    writeln('range=    ', range);
    writeln('cftfak=   ', cftfak);
    writeln('roimin=   ', roimin);
    writeln('roimax=   ', roimax);
    writeln('nregions= ', nregions);
    writeln('caluse=   ', caluse);
    writeln('calpoints=', calpoints);
    writeln('param=    ', param);
    writeln('offset=   ', offset);
    writeln('xdim=     ', xdim);
    writeln('bitshift= ', bitshift);
    writeln('active=   ', active);
    writeln('roipreset=', roipreset);
  end;
end;

procedure PrintDat(len: Cardinal);
  var i: Integer;
begin
  writeln('first 30 of ', len, ' datapoints:');
  for i:= 0 to 29 do
    writeln(Spec[i]);
end;

procedure help;
begin
  writeln('Commands:');
  writeln('Q     Quit');
  writeln('H     Help');
  writeln('S     Status');
  writeln('G     Settings');
  writeln('CHN=x Switch to CHN #x');
  writeln('D     Get Data');
  writeln('... more see command language in MPANT Help');
end;

function run(command : String) : LongInt;
begin
  run := 0;
  if command = 'H' then
  help
  else if command = 'Q' then
  begin
    run := 1;
  end
  else if command = 'S' then
  begin
    if @TStat <> nil then
    begin
      Err := TStat(Status, Adc);
      PrintStatus(Status);
    end;
  end
  else if command = 'G' then
  begin
    if @TGet <> nil then
    begin
        Err := TGet(Setting, Adc);
        PrintSetting(Setting);
      if Adc = 0 then
      begin
        Err := TMcs(MCSset, 0);
        PrintMCSSetting(MCSset);
      end;
    end;
  end
  else if AnsiPos('CHN=',command) = 1 then
  begin
     Val(String(PChar(command)+4), Adc, Err);
  end
  else if command = 'D' then
  begin
    if @TGet <> nil then
    begin
        Err := TGet(Setting, Adc);
        if @TDat <> nil then
        begin
          Err := TDat(Spec[0], Adc);
          PrintDat(Setting.range);
        end;
    end;
  end
  else
  begin
    if @TRun <> nil then
    begin
      TRun(0, PChar(command));
      writeln(command);
    end;
  end;
end;

begin
  SetLength(cmd, 100);
  Adc := 0;
  Handle := LoadLibrary('dmcs6.dll');
  if Handle <> 0 then
  begin
    @TGet := GetProcAddress(Handle, 'GetSettingData');
    @TStat := GetProcAddress(Handle, 'GetStatusData');
    @TRun := GetProcAddress(Handle, 'RunCmd');
    @TCnt := GetProcAddress(Handle, 'LVGetCnt');
    @TRoi := GetProcAddress(Handle, 'LVGetRoi');
    @TDat := GetProcAddress(Handle, 'LVGetDat');
    @TStr := GetProcAddress(Handle, 'LVGetStr');
    @TServ := GetProcAddress(Handle, 'ServExec');
    @TNewStat := GetProcAddress(Handle, 'GetStatus');
    @TDatset := GetProcAddress(Handle, 'GetDatSetting');
    @TMCS := GetProcAddress(Handle, 'GetMCSSetting');

    if @TNewStat <> nil then
      Err := TNewStat(0);

 {   if @TStat <> nil then
    begin
      Err := TStat(Status, 0);
      PrintStatus(Status);
    end;

    if @TGet <> nil then
    begin
      Err := TGet(Setting, 0);
      PrintSetting(Setting);
    end; }
    help;

    repeat
      readln(cmd);
    until run(cmd) <> 0;

    FreeLibrary(Handle);
  end;
end.



