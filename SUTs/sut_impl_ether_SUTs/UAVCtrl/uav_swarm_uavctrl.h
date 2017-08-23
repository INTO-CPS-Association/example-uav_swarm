
#ifndef _UAV_SWARM_UAVCTRL_H_
#define _UAV_SWARM_UAVCTRL_H_

#include "type1.h"
#include "time1.h"

// idx is 1 or 2, to get 0x1E ox 0x2E where 0xE means global controller
#define TARGET_ADDR(idx) ((idx == 1)? 0x1E: 0x2E)
#define CUR_ADDR(idx) ((idx == 1)? 0xF2: 0xF1) 

typedef struct {
	int addr;
	double payload[3];
} package_t;

/** Initialize SUT */
void sut_init();

/** Run SUT (one step) */
void sut_run(
	int uav_no,
	// from UAV
	double velX, double velY, double velZ, 
	double posX, double posY, double posZ, double batteryCharge, 
	// from Ether (Global Controller or other UAV Controllers)
	int UAVout1a, double UAVout1p1, double UAVout1p2, double UAVout1p3, 
	int UAVout2a, double UAVout2p1, double UAVout2p2, double UAVout2p3, 
	int *UAVin1a, double* UAVin1p1, double* UAVin1p2, double* UAVin1p3,
	double *throttleOut, double *pitchOut, double *rollOut, double *yawOut
);

#endif /* _UAV_SWARM_UAVCTRL_H_ */
