
#ifndef _TRACE_H_
#define _TRACE_H_
#include <stdarg.h>

#define DEBUG	1

int dbg_init(char *filename);
void dbg_printf(const char *fmt, ...);

#endif /* _TRACE_H_ */
