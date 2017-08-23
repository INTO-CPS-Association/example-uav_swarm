
#ifndef _UAV_SWARM_CTRL_H_
#define _UAV_SWARM_CTRL_H_

#include "type1.h"
#include "time1.h"

/** Initialize SUT */
void sut_init();

/** Run SUT (one step) */
void sut_run(double targetX1, double targetY1, double targetZ1, 
		double velX1, double velY1, double velZ1,
		double posX1, double posY1, double posZ1, double batteryCharge1, 
		double targetX2, double targetY2, double targetZ2, 
		double velX2, double velY2, double velZ2,
		double posX2, double posY2, double posZ2, double batteryCharge2, 
		double *throttleOut1, double *pitchOut1, double *rollOut1, double *yawOut1,
		double *throttleOut2, double *pitchOut2, double *rollOut2, double *yawOut2);


#endif /* _UAV_SWARM_CTRL_H_ */
