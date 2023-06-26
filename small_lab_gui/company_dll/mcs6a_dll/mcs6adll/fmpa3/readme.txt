FMPA3.DLL - DLL to communicate with MPANT for customer-calculated spectra
=========================================================================

Installation: Copy the FMPA3.DLL into the working directory (usually C:\MPA3).

Use: This DLL allows to calculate spectra and to display it with the MPANT program.
     Select a single spectra and open the Display options dialog. Press then the
     button labeled "Custom formula...". A dialog box "Custom-transformed spectra"
     is opened. Here the formula for the calculation can be selected and the 
     parameters can be edited. A new display window showing the calculated spectra 
     can be created. Error Bars can be activated in the display options dialog, for
     the calculation of the error bars also the DLL is used. 

Example: The supplied DLL is for acquisitions marked by a tag bit in a high bit
     of the ADC interface. It allows to calculate the Sum=x+x', Difference=x-x'
     and relative difference Delta=F*(x-x')/(x+x') of spectra marked by the tag bit.


