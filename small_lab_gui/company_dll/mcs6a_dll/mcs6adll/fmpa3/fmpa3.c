/***************************************************************************
  MODUL:    FMPA3.C
  PURPOSE:  DLL to communicate with MPANT, Custom-transformed spectra
****************************************************************************/

#include "windows.h"
#include <string.h>
#include <stdio.h>
#include <math.h>
#include "fmpa3.h"

// increase NFORMULAS if you add a new formula
#define NFORMULAS 5

#pragma data_seg("fmpa3sh")
int initialized=0;
CUSTFORMPAR custformpar[8]={{0}};
CUSTFORMTXT custformtxt[8]={{0}};
#pragma data_seg()


// auxiliary routines to save and read parameters, don't change...
static int freadstr(FILE *stream, char *buff, int buflen)
{
  int i=0,ic;

  while ((ic=getc(stream)) != 10) {
    if (ic == EOF) {
      buff[i]='\0';
      return 1;
    }
    if (ic == 13) ic=0;
    buff[i]=(char)ic;
    i++;
    if (i==buflen-1) break;
  }
  buff[i]='\0';
  return 0;
}

static int config(char *item, int *nform)
{
  int ret=0;

  if (!strnicmp("[Formula #", item, 10)) {
    sscanf(item+10, "%d", nform);
	if (*nform > 0) (*nform)--;
    return ret;
  }
  else if(!strnicmp("title=", item, 6)) {
    strcpy(custformtxt[*nform].shorttxt, item+6);
    return ret;
  }
  else if(!strnicmp("range=", item, 6)) {
    sscanf(item+6, "%d", &custformpar[*nform].range);
    return ret;
  }
  else if(!strnicmp("par1=", item, 5)) {
    sscanf(item+5, "%d", &custformpar[*nform].par1);
    return ret;
  }
  else if(!strnicmp("par2=", item, 5)) {
    sscanf(item+5, "%d", &custformpar[*nform].par2);
    return ret;
  }
  else if(!strnicmp("par3=", item, 5)) {
    sscanf(item+5, "%d", &custformpar[*nform].par3);
    return ret;
  }
  else if(!strnicmp("par4=", item, 5)) {
    sscanf(item+5, "%d", &custformpar[*nform].par4);
    return ret;
  }
  return 1;
}

static void getparams()
{ 
  int nform=0;
  FILE *f;
  char item[256];
  f = fopen("custform.txt", "rb");
  if (!f) return;
  while(!freadstr(f,item,256)) {
    config(item, &nform);
  }
  fclose(f);
}

static void saveparams()
{
  int k;
  FILE *f;
  f = fopen("custform.txt", "wt");
  for (k=0; k<NFORMULAS; k++) {
    fprintf(f,"[Formula #%d]\n", k+1);
	fprintf(f,"title=%s\n",custformtxt[k].shorttxt);
	fprintf(f,"range=%ld\n",custformpar[k].range);
    if (!(custformtxt[k].par1txt[0])) continue;
	fprintf(f,"par1=%ld\n",custformpar[k].par1);
    if (!(custformtxt[k].par2txt[0])) continue;
	fprintf(f,"par2=%ld\n",custformpar[k].par2);
    if (!(custformtxt[k].par3txt[0])) continue;
	fprintf(f,"par3=%ld\n",custformpar[k].par3);
    if (!(custformtxt[k].par4txt[0])) continue;
	fprintf(f,"par4=%ld\n",custformpar[k].par4);
  }
  fclose(f);
}
// ...auxiliary routines to save and read parameters, don't change

// Initialization, modify it if you add a new formula
static void inicustform()
{
  initialized=1;
  // custform[0]: Sum x+x'
  // default parameters:
  custformpar[0].range = 4096;	// default spectra length, max. 16384 with tagbit=14
  custformpar[0].par1  = 14;	// Tagbit
  strcpy(custformtxt[0].formtxt,"Sum x + x' \nx' is marked by a Tag Bit.");
  strcpy(custformtxt[0].shorttxt,"Sum"); // short formula title
  strcpy(custformtxt[0].par1txt,"&Tag Bit:");
  strcpy(custformtxt[0].par3txt, "");
  strcpy(custformtxt[0].par4txt, "");
  // custform[1]: Diff x-x'
  // default parameters:
  custformpar[1].range = 4096;	// default spectra length, max. 16384 with tagbit=14
  custformpar[1].par1  = 14;	// Tagbit
  strcpy(custformtxt[1].formtxt,"Diff x - x' \nx' is marked by a Tag Bit.");
  strcpy(custformtxt[1].shorttxt,"Diff"); // short formula title
  strcpy(custformtxt[1].par1txt,"&Tag Bit:");
  strcpy(custformtxt[1].par3txt, "");
  strcpy(custformtxt[1].par4txt, "");
  // custform[2]: F * (x-x') / (x+x')
  // default parameters:
  custformpar[2].range = 4096;  // default spectra length, max. 16384
  custformpar[2].par1  = 14;	// Tagbit
  custformpar[2].par2  = 1000;  // factor F
  strcpy(custformtxt[2].formtxt,"Delta F * (x - x') / (x + x') \nx' is marked by a Tag Bit.");
  strcpy(custformtxt[2].shorttxt,"Delta");  // short formula title
  strcpy(custformtxt[2].par1txt, "&Tag Bit:");
  strcpy(custformtxt[2].par2txt, "&Factor F:");
  strcpy(custformtxt[2].par3txt, "");
  strcpy(custformtxt[2].par4txt, "");
  // custform[3]: Min(x) (y)    
  // default parameters:
  custformpar[3].range = 4096;  // default spectra length
  custformpar[3].par1 = 128;    // xdim
  strcpy(custformtxt[3].formtxt,"Min(x) as a function of y \nDisplay original as Single.");
  strcpy(custformtxt[3].shorttxt,"Min(x)");  // short formula title
  strcpy(custformtxt[3].par1txt, "&Xdim:");
  // custform[4]: /x
  // default parameters:
  custformpar[4].range = 4096;  // default spectra length
  strcpy(custformtxt[4].formtxt, "Reverse direction of x.");
  strcpy(custformtxt[4].shorttxt, "/x");
  getparams();
}

// DLL Entry Function
BOOL APIENTRY DllMain(HANDLE hInst, DWORD ul_reason_being_called, LPVOID lpReserved)
{
    if (!initialized) inicustform();
    return 1;
        UNREFERENCED_PARAMETER(hInst);
        UNREFERENCED_PARAMETER(ul_reason_being_called);
        UNREFERENCED_PARAMETER(lpReserved);
}

// DLL Function to read saved parameters
int APIENTRY GetCustomForm(int n, CUSTFORMPAR *custf, CUSTFORMPTXT *custt)
{
  if (n >= 8) return 0;
  memcpy(custf, &custformpar[n], sizeof(CUSTFORMPAR));
  //memcpy(custt, &custformtxt[n], sizeof(CUSTFORMTXT));
  custt->pformtxt = custformtxt[n].formtxt;      // description
  custt->pshorttxt = custformtxt[n].shorttxt;    // short formula title
  custt->ppar1txt  = custformtxt[n].par1txt;     // title par1 (tagbit)
  custt->ppar2txt  = custformtxt[n].par2txt;     // title par2 (factor)
  custt->ppar3txt  = custformtxt[n].par3txt;     // title par3 
  custt->ppar4txt  = custformtxt[n].par4txt;     // title par4 
  return custformpar[n].range;
}

// DLL function to save edited parameters
int APIENTRY SaveCustomForm(int n, CUSTFORMPAR *custf)
{
  if (n >= 8) return 0;
  memcpy(&custformpar[n], custf, sizeof(CUSTFORMPAR));
  saveparams();
  return custformpar[n].range;
}

// DLL function to calculate a spectra, modify it if you add a new formula
int APIENTRY CalcForm(int n, CUSTFORMPAR *custf, unsigned long *dat, long x, long *result, long ndim)
{
  long xx;
  switch(n) {
  case 1:
	  if ((x < 0) || (x >= custf->range)) goto errout;
	  xx = x | (1L<<(custf->par1));
	  if (xx >= ndim) goto errout;
	  *result = dat[x] + dat[xx];
	  break;
  case 2:
	  if ((x < 0) || (x >= custf->range)) goto errout;
	  xx = x | (1L<<(custf->par1));
	  if (xx >= ndim) goto errout;
	  *result = dat[x] - dat[xx];
	  break;
  case 3: {
	    double v, v1;
	    if ((x < 0) || (x >= custf->range)) goto errout;
	    v = dat[x];
		xx = x | (1L<<(custf->par1));
	    if (xx >= ndim) goto errout;
	    v1 = dat[xx];
	    *result = (long)(custf->par2 * (v-v1)/(v+v1));
	    break;
	  }
  case 4: {
	    long offset = x * custf->par1;
		long v=0;
	    if ((x < 0) || (x >= custf->range)) goto errout;
		if (offset + custf->par1 > ndim) goto errout;
		for (xx=0; xx<custf->par1; xx++) {
		  if (dat[offset+xx] == 0) continue;
		  v = xx;
		  break;
		}
        *result = v;
		break;
	  }
  case 5: {
	    xx = custf->range - 1 - x;
		if (xx < 0) goto errout;
		if (xx >= custf->range) goto errout;
	    *result = dat[xx];
	    break;
	  }
  default:
	  goto errout;
  }
  return 1;
errout:
  *result = 0;
  return 0;
}

// DLL function to calculate the error bars for the calculated spectra, 
// modify it if you add a new formula
int APIENTRY CalcErr(int n, CUSTFORMPAR *custf, unsigned long *dat, long x, long val, double *result, long ndim)
{
  long xx;
  switch(n) {
  case 1:
  case 4:
  case 5:
	  if ((x < 0) || (x >= custf->range) || (val < 0)) goto errout;
	  *result = sqrt((double)val);
	  break;
  case 2: {
	    double v, v1, v2;
	    if ((x < 0) || (x >= custf->range)) goto errout;
	    v = dat[x];
		xx = x | (1L<<(custf->par1));
	    v1 = dat[xx];
	    if (xx >= ndim) goto errout;
		v2 = v+v1;
	    *result = sqrt((double)v2);
	    break;
	  }
  case 3: {
	    double v, v1, v2;
	    if ((x < 0) || (x >= custf->range)) goto errout;
	    v = dat[x];
		xx = x | (1L<<(custf->par1));
	    v1 = dat[xx];
	    if (xx >= ndim) goto errout;
		v2 = v+v1;
	    *result = custf->par2 * 2.* sqrt(v*v1*v2)/(v2*v2);
	    break;
	  }
  default:
	  goto errout;
  }
  return 1;
errout:
  *result = 0;
  return 0;
}
