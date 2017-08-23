#include "trace.h"
#include "uav_swarm_uavctrl.h"
#include "uav_swarm_uav_ctrl.h"

static VSTimer_t t;

/** Initialize SUT */
void sut_init()
{
	dbg_init("sut.log");
	uav_ctrl_init();
	reset(&t);
}

static package_t curPosUAV;

// local backup
static int local_GEin1a;
static double local_GEin1p1;
static double local_GEin1p2;
static double local_GEin1p3;

static double local_throttle = 0;
static double local_pitch = 0;
static double local_roll = 0;
static double local_yaw = 0;

static double local_targetX = 0;
static double local_targetY = 0;
static double local_targetZ = 0;

/** Run SUT (one step) */
void sut_run(
	int uav_no, /*1 or 2*/
	// from UAV
	double velX, double velY, double velZ, 
	double posX, double posY, double posZ, double batteryCharge, 
	// from Ether (Global Controller or other UAV Controllers)
	int UAVout1a, double UAVout1p1, double UAVout1p2, double UAVout1p3, 
	int UAVout2a, double UAVout2p1, double UAVout2p2, double UAVout2p3, 
	int *UAVin1a, double* UAVin1p1, double* UAVin1p2, double* UAVin1p3,
	double *throttleOut, double *pitchOut, double *rollOut, double *yawOut)
{
	dbg_printf(" %14s >>> (incoming packages: 1: 0x%x, %.8f, %.8f, %.8f, 2:0x%x, %.8f, %.8f, %.8f) \n", 
		__FILE__, UAVout1a, UAVout1p1, UAVout1p2, UAVout1p3, 
				  UAVout2a, UAVout2p1, UAVout2p2, UAVout2p3);
	
	if(!elapsed(&t, __ms(40)))
	{
		*UAVin1a = local_GEin1a;
		*UAVin1p1 = local_GEin1p1;
		*UAVin1p2 = local_GEin1p2;
		*UAVin1p3 = local_GEin1p3;
		*throttleOut = local_throttle;
		*pitchOut = local_pitch;
		*rollOut = local_roll;
		*yawOut = local_yaw;
		return;
	}

	reset(&t);

	dbg_printf(" %14s >>> (incoming packages: 1: 0x%x, %.8f, %.8f, %.8f, 2:0x%x, %.8f, %.8f, %.8f) \n", 
		__FILE__, UAVout1a, UAVout1p1, UAVout1p2, UAVout1p3, 
				  UAVout2a, UAVout2p1, UAVout2p2, UAVout2p3);
	// check incoming packages for target position and current position
	// target positions always in the first incoming package, and current positions in the second package
/*	if(UAVout1a == TARGET_ADDR(uav_no))
	{
		local_targetX = UAVout1p1;
		local_targetY = UAVout1p2;
		local_targetZ = UAVout1p3;
	}
	
	if (UAVout2a == CUR_ADDR(uav_no))
	{
		curPosUAV.addr = UAVout2a;
		curPosUAV.payload[0] = UAVout2p1;
		curPosUAV.payload[1] = UAVout2p2;
		curPosUAV.payload[2] = UAVout2p3;
	}
*/	
	
	// check incoming packages for target position and current position
	if((UAVout1a == TARGET_ADDR(uav_no)) && (UAVout2a == CUR_ADDR(uav_no)))
	{
		local_targetX = UAVout1p1;
		local_targetY = UAVout1p2;
		local_targetZ = UAVout1p3;
		curPosUAV.addr = UAVout2a;
		curPosUAV.payload[0] = UAVout2p1;
		curPosUAV.payload[1] = UAVout2p2;
		curPosUAV.payload[2] = UAVout2p3;
	}
	else if ((UAVout1a == TARGET_ADDR(uav_no)) && (UAVout2a != CUR_ADDR(uav_no)))
	{
		local_targetX = UAVout1p1;
		local_targetY = UAVout1p2;
		local_targetZ = UAVout1p3;
	}
	else if ((UAVout1a != TARGET_ADDR(uav_no)) && (UAVout2a == CUR_ADDR(uav_no)))
	{
		curPosUAV.addr = UAVout2a;
		curPosUAV.payload[0] = UAVout2p1;
		curPosUAV.payload[1] = UAVout2p2;
		curPosUAV.payload[2] = UAVout2p3;
	}
	else // if no incoming package
	{
		dbg_printf(" %14s (No incoming packages) \n", __FILE__ );
	}
	

	uav_ctrl(uav_no - 1, local_targetX, local_targetY, local_targetZ,
			velX, velY, velZ, posX, posY, posZ, batteryCharge,
			throttleOut, pitchOut, rollOut, yawOut);
	local_throttle = *throttleOut;
	local_pitch = *pitchOut;
	local_roll = *rollOut;
	local_yaw = *yawOut;
	
	// Send out current position
	*UAVin1a = local_GEin1a = 0xF0 | uav_no; // broadcast
	*UAVin1p1 = local_GEin1p1 = posX;
	*UAVin1p2 = local_GEin1p2 = posY;
	*UAVin1p3 = local_GEin1p3 = posZ;
}
