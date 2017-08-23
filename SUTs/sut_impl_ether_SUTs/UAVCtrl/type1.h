#ifndef _TYPE1_H_
#define _TYPE1_H_

#include <math.h>
#define TRUE	1
#define FALSE	0
typedef unsigned char BOOLEAN;

#define ERR		1E-8

#define dequal(a,b) (fabs(a-b) <= ERR) 
#define dnequal(a,b) (fabs(a-b) > ERR) 

#endif /* _TYPE1_H_ */
