#include "trace.h"
#include "time1.h"
#include "uav_swarm_global_ctrl.h"

static VSTimer_t t;

void global_ctrl_init()
{
	reset(&t);
}

static BOOLEAN firstCall = 1;
static double targetPos[2][3] = {{0, 0, 0}, {0, 0, 0}};

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
	)
{
	BOOLEAN diff1 = FALSE;
	BOOLEAN diff2 = FALSE;

	if(firstCall) 
    {
		if(!elapsed(&t, __ms(40))) 
		{
			// copy the local copy to output and new inputs are discarded
			*tarX1 = targetX1;
			*tarY1 = targetY1;
			*tarZ1 = targetZ1;
			*tarX2 = targetX2;
			*tarY2 = targetY2;
			*tarZ2 = targetZ2;
			return 0;
		}
	}
	else
	{
		if(!elapsed(&t, __ms(40))) 
		{
			// copy the local copy to output and new inputs are discarded
			*tarX1 = targetPos[0][0];
			*tarY1 = targetPos[0][1];
			*tarZ1 = targetPos[0][2];
			*tarX2 = targetPos[1][0];
			*tarY2 = targetPos[1][1];
			*tarZ2 = targetPos[1][2];		
			return 0;
		}
	}


	if(dnequal(targetX1, targetPos[0][0]) ||
	   dnequal(targetY1, targetPos[0][1]) ||
	   dnequal(targetZ1, targetPos[0][2]) )
		diff1 = TRUE;
	
	if(dnequal(targetX2, targetPos[1][0]) ||
	   dnequal(targetY2, targetPos[1][1]) ||
	   dnequal(targetZ2, targetPos[1][2]) )
		diff2 = TRUE;

	if(diff1)
		dbg_printf("%15s >>> (targetX1:%.8f, targetY1:%.8f, targetZ1:%.8f)\n", "[Global_Ctrl]",
			targetX1, targetY1, targetZ1);
	
	if(diff2)
		dbg_printf("%15s >>> (targetX2:%.8f, targetY2:%.8f, targetZ2:%.8f)\n", "[Global_Ctrl]",
			targetX2, targetY2, targetZ2);
	
	reset(&t);
	firstCall = 0;
	
	// get target positions from last stored positions to have a 40ms delay
	// in order that this does match with the test model where target positions 
	// wouldn't be seen by UAV controller immediately
	*tarX1 = targetPos[0][0];
	*tarY1 = targetPos[0][1];
	*tarZ1 = targetPos[0][2];
	*tarX2 = targetPos[1][0];
	*tarY2 = targetPos[1][1];
	*tarZ2 = targetPos[1][2];
	
	// update stored local values by new incoming positions
	targetPos[0][0] = targetX1;
	targetPos[0][1] = targetY1;
	targetPos[0][2] = targetZ1;
	targetPos[1][0] = targetX2;
	targetPos[1][1] = targetY2;
	targetPos[1][2] = targetZ2;

	if(diff1)
		dbg_printf("%15s <<< (tarX1:%.8f, tarY1:%.8f, tarZ1:%.8f)\n", "[Global_Ctrl]",
			*tarX1, *tarY1, *tarZ1);
	if(diff2)
		dbg_printf("%15s <<< (tarX2:%.8f, tarY2:%.8f, tarZ2:%.8f)\n", "[Global_Ctrl]",
			*tarX2, *tarY2, *tarZ2);

	return 1;
}
