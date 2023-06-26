Using the DMCS6.DLL from Matlab
================================

It does not work, to load the DMCS6.DLL in Matlab via loadlibrary
and direct call DLL functions. You have to make mex files as
an intermediate layer.
 
An example is the supplied mxruncmd.c. It can be used to send
commands to the server via the RunCmd DLL function. Try the example:
0. Copy the files dmcs6.h, struct.h, mxruncmd.c
   into C:\MCS6A
1. Start the MCS6A Server (and MPANT) program.
2. Start Matlab
3. Set the current directory in Matlab to C:\MCS6A via the 
   Current folder bar at the top.
4. To compile the mex file mxruncmd.mexw32 from mxruncmd.c,
setup the compiler with command

mex -setup

and compile by

mex mxruncmd.c


5. Enter the command
   mxruncmd('run test.ctl')

You can also define string commands and use them, for example

s = 'erase'
mxruncmd(s)


