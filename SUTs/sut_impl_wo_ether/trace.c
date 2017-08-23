#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "time1.h"
#include "trace.h"

static FILE* f = NULL;

int dbg_init(char *filename)
{
	f = fopen(filename, "w+");
	if(f != NULL)
		return 1;
	return 0;
}

void dbg_printf(const char *format, ...)
{
	if(DEBUG)
	{
		char newformat[1024]; 
		long long tt = gettime();

		snprintf(newformat, sizeof(newformat), "%10lld %s", tt, format);

		va_list args;
    	va_start(args, format);

		// snprintf(newformat, sizeof(newformat), format, args);
		if(f != NULL) 
			vfprintf(f, newformat, args);
		else
			vfprintf(stderr, newformat, args);

    	va_end(args);

		fflush(f);
	}
}

