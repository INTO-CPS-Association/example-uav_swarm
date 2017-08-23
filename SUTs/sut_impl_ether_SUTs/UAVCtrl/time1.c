#include "time1.h"

long long gettime ()
{
  struct timeval now;
  ti_gettimeofday( &now, NULL );
  return (now.tv_sec * 1000000 + now.tv_usec);
}

void reset( VSTimer_t* timer)
{
  struct timeval now;
  ti_gettimeofday( &now, NULL );
  *timer = now.tv_sec * 1000000 + now.tv_usec;
}

BOOLEAN elapsed( VSTimer_t* timer, long usec )
{
  struct timeval now;
  long long usec_now;

  ti_gettimeofday( &now, NULL );
  usec_now = now.tv_sec * 1000000 + now.tv_usec;
  return ( ( usec_now - (*timer) ) >= usec );
}
