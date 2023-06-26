typedef struct {
  long range;		// length
  long par1;		// tagbit
  long par2;		// factor
  long par3;		// reserved
  long par4;		// reserved
} CUSTFORMPAR;

typedef struct {
  char formtxt[256]; // description
  char shorttxt[64];  // short formula title
  char par1txt[64];	  // title par1 (tagbit)
  char par2txt[64];   // title par2 (factor)
  char par3txt[64];   // title par3 
  char par4txt[64];   // title par4 
} CUSTFORMTXT;

typedef struct {
  char *pformtxt;    // description
  char *pshorttxt;    // short formula title
  char *ppar1txt;	  // title par1 (tagbit)
  char *ppar2txt;     // title par2 (factor)
  char *ppar3txt;     // title par3 
  char *ppar4txt;     // title par4 
} CUSTFORMPTXT;

int APIENTRY GetCustomForm(int n, CUSTFORMPAR *custf, CUSTFORMPTXT *custt);
int APIENTRY SaveCustomForm(int n, CUSTFORMPAR *custf);
int APIENTRY CalcForm(int n, CUSTFORMPAR *custf, unsigned long *dat, long x, 
					  long *result, long ndim);
int APIENTRY CalcErr(int n, CUSTFORMPAR *custf, unsigned long *dat, long x, long val, 
					 double *result, long ndim);
