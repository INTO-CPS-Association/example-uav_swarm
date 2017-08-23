#include "trace.h"
#include "uav_swarm_ctrl.h"
#include "uav_swarm_global_ctrl.h"
#include "uav_swarm_uav_ctrl.h"

/** Initialize SUT */
void sut_init()
{
	dbg_init("sut.log");
	global_ctrl_init();
	uav_ctrl_init();
}

/** Run SUT (one step) */
void sut_run(double targetX1, double targetY1, double targetZ1, 
		double velX1, double velY1, double velZ1,
		double posX1, double posY1, double posZ1, double batteryCharge1, 
		double targetX2, double targetY2, double targetZ2, 
		double velX2, double velY2, double velZ2,
		double posX2, double posY2, double posZ2, double batteryCharge2, 
		double *throttleOut1, double *pitchOut1, double *rollOut1, double *yawOut1,
		double *throttleOut2, double *pitchOut2, double *rollOut2, double *yawOut2)
{
	double tarX1, tarY1, tarZ1;
	double tarX2, tarY2, tarZ2;
		
	global_ctrl(targetX1, targetY1, targetZ1, targetX2, targetY2, targetZ2, 
		&tarX1, &tarY1, &tarZ1, &tarX2, &tarY2, &tarZ2);
	uav_ctrl(0, tarX1, tarY1, tarZ1, velX1, velY1, velZ1, 
		posX1, posY1, posZ1, batteryCharge1, 
		throttleOut1, pitchOut1, rollOut1, yawOut1);
	uav_ctrl(1, tarX2, tarY2, tarZ2, velX2, velY2, velZ2, 
		posX2, posY2, posZ2, batteryCharge2, 
		throttleOut2, pitchOut2, rollOut2, yawOut2);
}
