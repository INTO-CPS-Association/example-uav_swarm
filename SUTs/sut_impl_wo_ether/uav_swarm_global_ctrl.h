#ifndef _UAV_SWARM_GLOBAL_CTRL_H_
#define _UAV_SWARM_GLOBAL_CTRL_H_

#include "type1.h"

void global_ctrl_init();

int global_ctrl(
	double targetX1, 
	double targetY1,
	double targetZ1,
	double targetX2, 
	double targetY2,
	double targetZ2,
	double *tarX1, 
	double *tarY1,
	double *tarZ1,
	double *tarX2, 
	double *tarY2,
	double *tarZ2
	);

#endif /* _UAV_SWARM_GLOBAL_CTRL_H_ */
