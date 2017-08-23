#include "trace.h"
#include "uav_swarm_globalctrl.h"

static VSTimer_t t;
static stages_enum st = SEND_TARGET1;

/** Initialize SUT */
void sut_init()
{
	dbg_init("sut.log");
	reset(&t);
}

static int local_GEin1a;
static double local_GEin1p1;
static double local_GEin1p2;
static double local_GEin1p3;

static package_t curPosUAV1;
static package_t curPosUAV2;

/** Run SUT (one step) */
void sut_run(double targetX1, double targetY1, double targetZ1, 
			double targetX2, double targetY2, double targetZ2, 
			int GEout1a, double GEout1p1, double GEout1p2, double GEout1p3, 
			int GEout2a, double GEout2p1, double GEout2p2, double GEout2p3, 
			int *GEin1a, double* GEin1p1, double* GEin1p2, double* GEin1p3)
{
	if(!elapsed(&t, __ms(15)))
	{
		// just return with last output
		*GEin1a = local_GEin1a;
		*GEin1p1 = local_GEin1p1;
		*GEin1p2 = local_GEin1p2;
		*GEin1p3 = local_GEin1p3;
		return;
	}
	else if(elapsed(&t, __ms(15)) && !elapsed(&t, __ms(30)))
	{
		if(st == SEND_TARGET1)
		{
			// send target position of UAV1 to Ether
			*GEin1a = 0x1E;
			*GEin1p1 = targetX1;
			*GEin1p2 = targetY1;
			*GEin1p3 = targetZ1;
			local_GEin1a = 0x1E;
			local_GEin1p1 = targetX1;
			local_GEin1p2 = targetY1;
			local_GEin1p3 = targetZ1;
			st = SEND_TARGET2;
			dbg_printf("%15s >>> (send target position to UAV1 Controller: addr: 0x%x, payload:%.8f, %.8f, %.8f)\n", 
				__FUNCTION__, local_GEin1a, local_GEin1p1, local_GEin1p2, local_GEin1p3);
		}
		else 
		{
			*GEin1a = local_GEin1a;
			*GEin1p1 = local_GEin1p1;
			*GEin1p2 = local_GEin1p2;
			*GEin1p3 = local_GEin1p3;
			return;
		}
	}
	else if(elapsed(&t, __ms(30)) && !elapsed(&t, __ms(40)))
	{
		if(st == SEND_TARGET2)
		{
			// send target position of UAV1 to Ether
			*GEin1a = 0x2E;
			*GEin1p1 = targetX2;
			*GEin1p2 = targetY2;
			*GEin1p3 = targetZ2;
			local_GEin1a = 0x2E;
			local_GEin1p1 = targetX2;
			local_GEin1p2 = targetY2;
			local_GEin1p3 = targetZ2;
			st = SEND_PROCESS_CUR;
			dbg_printf("%15s >>> (send target position to UAV2 Controller: addr: 0x%x, payload:%.8f, %.8f, %.8f)\n", 
				__FUNCTION__, local_GEin1a, local_GEin1p1, local_GEin1p2, local_GEin1p3);
		}
		else 
		{
			*GEin1a = local_GEin1a;
			*GEin1p1 = local_GEin1p1;
			*GEin1p2 = local_GEin1p2;
			*GEin1p3 = local_GEin1p3;
			return;
		}
	}
	else if(elapsed(&t, __ms(40)))
	{
		// check incoming packages
		reset(&t);
		st = SEND_TARGET1;

		if(GEout1a == 0xF1)
		{
			if(GEout2a == 0xF2)
			{
				curPosUAV1.addr = GEout1a;
				curPosUAV1.payload[0] = GEout1p1;
				curPosUAV1.payload[1] = GEout1p2;
				curPosUAV1.payload[2] = GEout1p3;
				curPosUAV2.addr = GEout2a;
				curPosUAV2.payload[0] = GEout2p1;
				curPosUAV2.payload[1] = GEout2p2;
				curPosUAV2.payload[2] = GEout2p3;
				dbg_printf("%15s >>> (update current positions of UAV1 (%.8f, %.8f, %.8f) and UAV2 (%.8f, %.8f, %.8f) \n", 
					__FUNCTION__, curPosUAV1.payload[0], curPosUAV1.payload[1], curPosUAV1.payload[2], 
					curPosUAV2.payload[0], curPosUAV2.payload[1], curPosUAV2.payload[2]);
			}
			else
			{
				curPosUAV1.addr = GEout1a;
				curPosUAV1.payload[0] = GEout1p1;
				curPosUAV1.payload[1] = GEout1p2;
				curPosUAV1.payload[2] = GEout1p3;
				dbg_printf("%15s >>> (update current positions of UAV1 (%.8f, %.8f, %.8f) \n", 
					__FUNCTION__, curPosUAV1.payload[0], curPosUAV1.payload[1], curPosUAV1.payload[2]);
			}
		}
		else 
		{
			if(GEout2a == 0xF2)
			{
				curPosUAV2.addr = GEout2a;
				curPosUAV2.payload[0] = GEout2p1;
				curPosUAV2.payload[1] = GEout2p2;
				curPosUAV2.payload[2] = GEout2p3;
				dbg_printf("%15s >>> (update current positions of UAV2 (%.8f, %.8f, %.8f) \n", 
					__FUNCTION__, curPosUAV2.payload[0], curPosUAV2.payload[1], curPosUAV2.payload[2]);
			}
			else
			{
				// no change
			}
		}
	}

	return;
}
