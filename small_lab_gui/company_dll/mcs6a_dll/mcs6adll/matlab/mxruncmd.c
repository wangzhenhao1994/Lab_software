/*=================================================================
 * based on mxmalloc.c in the matlabroot/extern/examples/mx folder 
 * 
 * This function takes a MATLAB string as an argument and copies it in 
 * NULL terminated ANSI C string.
 *
 * This is a MEX-file for MATLAB.  
 * Copyright 1984-2006 The MathWorks, Inc.
 * All rights reserved.
 *=================================================================*/

/* $Revision: 1.3.6.2 $ */
#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <time.h>

#undef DLL

#include "dmcs6.h"
#include "mex.h"

HMODULE  hDLL = 0;
IMPARUNCMD      lpRun=NULL;
   
void
mexFunction(int nlhs,mxArray *plhs[],int nrhs,const mxArray *prhs[])
{
    char *buf;
    mwSize buflen;
    int status;

    (void) plhs;    /* unused parameters */
    
    /* Check for proper number of input and output arguments */
    if (nrhs != 1) { 
	mexErrMsgTxt("One input argument required.");
    } 
    if (nlhs > 1) {
	mexErrMsgTxt("Too many output arguments.");
    }
    
    /* Check for proper input type */
    if (!mxIsChar(prhs[0]) || (mxGetM(prhs[0]) != 1 ) )  {
	mexErrMsgTxt("Input argument must be a string.");
    }
    
    /* Find out how long the input string is.  Allocate enough memory
       to hold the converted string.  NOTE: MATLAB stores characters
       as 2 byte unicode ( 16 bit ASCII) on machines with multi-byte
       character sets.  You should use mxChar to ensure enough space
       is allocated to hold the string */
    
    buflen = mxGetN(prhs[0])*sizeof(mxChar)+1;
    buf = mxMalloc(buflen);
    
    /* Copy the string data into buf. */ 
    status = mxGetString(prhs[0], buf, buflen);   
    mexPrintf("The input string is:  %s\n", buf);
    /* NOTE: You could add your own code here to manipulate 
       the string */

    hDLL = LoadLibrary("DMCS6.DLL");
    if(hDLL){
	  lpRun=(IMPARUNCMD)GetProcAddress(hDLL,"RunCmd");

      lpRun(0, buf);
      mexPrintf("The string after calling RunCmd is:  %s\n", buf);

	}

    FreeLibrary(hDLL);

	/* When finished using the string, deallocate it. */
    mxFree(buf);
    
}

