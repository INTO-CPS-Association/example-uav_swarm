#ifndef _UAV_SWARM_UAV_CTRL_H_
#define _UAV_SWARM_UAV_CTRL_H_

void uav_ctrl_init();

int uav_ctrl( 
	int index,
	double targetX1, 
	double targetY1, 
	double targetZ1, 
	double velX1, 
	double velY1, 
	double velZ1, 
	double posX1, 
	double posY1, 
	double posZ1, 
	double batteryCharge, 
	double *throttleOut1, 
	double *pitchOut1,
	double *rollOut1, 
	double *yawOut1);

#endif /* _UAV_SWARM_UAV_CTRL_H_ */
