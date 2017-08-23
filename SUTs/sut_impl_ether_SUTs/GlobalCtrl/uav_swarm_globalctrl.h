
#ifndef _UAV_SWARM_CTRL_H_
#define _UAV_SWARM_CTRL_H_

#include "type1.h"
#include "time1.h"

typedef enum {
	SEND_TARGET1,		// send target positions for UAV1
	SEND_TARGET2,		// send target positions for UAV2
	SEND_PROCESS_CUR	// process incoming current positions
} stages_enum;

typedef struct {
	int addr;
	double payload[3];
} package_t;

/** Initialize SUT */
void sut_init();

/** Run SUT (one step) */
void sut_run(double targetX1, double targetY1, double targetZ1, 
			double targetX2, double targetY2, double targetZ2, 
			int GEout1a, double GEout1p1, double GEout1p2, double GEout1p3, 
			int GEout2a, double GEout2p1, double GEout2p2, double GEout2p3, 
			int *GEin1a, double* GEin1p1, double* GEin1p2, double* GEin1p3);

#endif /* _UAV_SWARM_CTRL_H_ */
