#ifndef _TIME1_H_
#define _TIME1_H_
#include <time.h>
#include "type1.h"

#define __ms( t ) ( (t) * 1000 )

typedef long long VSTimer_t;

long long gettime ();
void reset( VSTimer_t* timer);
BOOLEAN elapsed( VSTimer_t* timer, long usec );

// -------------------------------------------------------------------------
extern int ti_gettimeofday(struct timeval *tv, struct timezone *tz);
// -------------------------------------------------------------------------
#endif /* _TIME1_H_ */
