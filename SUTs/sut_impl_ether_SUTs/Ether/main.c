#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

#include "uav_swarm_ether.h"
#include "trace.h"

int ti_gettimeofday(struct timeval *tv, struct timezone *tz){
	gettimeofday(tv, NULL);
	return 0; 
}


int main(int argc, char** argv) 
{
	int GEout1a; 
	double GEout1p1; 
	double GEout1p2;
	double GEout1p3;

	int GEout2a;
	double GEout2p1;
	double GEout2p2;
	double GEout2p3;

	int U1Eout1a;
	double U1Eout1p1;
	double U1Eout1p2;
	double U1Eout1p3;

	int U1Eout2a;
	double U1Eout2p1;
	double U1Eout2p2;
	double U1Eout2p3;

	int U2Eout1a;
	double U2Eout1p1;
	double U2Eout1p2;
	double U2Eout1p3;

	int U2Eout2a;
	double U2Eout2p1;
	double U2Eout2p2;
	double U2Eout2p3;

	sut_init();

	sleep(10);
	// send targets to UAV1
	sut_run(0x1E, 0, 1, 2, 
				0, 3, 4, 5, 
				0, 6, 7, 8, 
				&GEout1a,  &GEout1p1,  &GEout1p2,  &GEout1p3,
				&GEout2a,  &GEout2p1,  &GEout2p2,  &GEout2p3,
				&U1Eout1a,  &U1Eout1p1,  &U1Eout1p2,  &U1Eout1p3,
				&U1Eout2a,  &U1Eout2p1,  &U1Eout2p2,  &U1Eout2p3,
				&U2Eout1a,  &U2Eout1p1,  &U2Eout1p2,  &U2Eout1p3,
				&U2Eout2a,  &U2Eout2p1,  &U2Eout2p2,  &U2Eout2p3
			   );
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 1, U1Eout1a, U1Eout1p1, U1Eout1p2, U1Eout1p3, U1Eout2a, U1Eout2p1, U1Eout2p2, U1Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 2, U2Eout1a, U2Eout1p1, U2Eout1p2, U2Eout1p3, U2Eout2a, U2Eout2p1, U2Eout2p2, U2Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 14, GEout1a, GEout1p1, GEout1p2, GEout1p3, GEout2a, GEout2p1, GEout2p2, GEout2p3);
	sleep(10);
	// send targets to UAV2
	sut_run(0x2E, 0, 1, 2, 
				0, 3, 4, 5, 
				0, 6, 7, 8, 
				&GEout1a,  &GEout1p1,  &GEout1p2,  &GEout1p3,
				&GEout2a,  &GEout2p1,  &GEout2p2,  &GEout2p3,
				&U1Eout1a,  &U1Eout1p1,  &U1Eout1p2,  &U1Eout1p3,
				&U1Eout2a,  &U1Eout2p1,  &U1Eout2p2,  &U1Eout2p3,
				&U2Eout1a,  &U2Eout1p1,  &U2Eout1p2,  &U2Eout1p3,
				&U2Eout2a,  &U2Eout2p1,  &U2Eout2p2,  &U2Eout2p3
			   );
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 1, U1Eout1a, U1Eout1p1, U1Eout1p2, U1Eout1p3, U1Eout2a, U1Eout2p1, U1Eout2p2, U1Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 2, U2Eout1a, U2Eout1p1, U2Eout1p2, U2Eout1p3, U2Eout2a, U2Eout2p1, U2Eout2p2, U2Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 14, GEout1a, GEout1p1, GEout1p2, GEout1p3, GEout2a, GEout2p1, GEout2p2, GEout2p3);
	sleep(10);
	
	// broadcast from 1
	sut_run(0, 0, 1, 2, 
				0xF1, 3, 4, 5, 
				0, 6, 7, 8, 
				&GEout1a,  &GEout1p1,  &GEout1p2,  &GEout1p3,
				&GEout2a,  &GEout2p1,  &GEout2p2,  &GEout2p3,
				&U1Eout1a,  &U1Eout1p1,  &U1Eout1p2,  &U1Eout1p3,
				&U1Eout2a,  &U1Eout2p1,  &U1Eout2p2,  &U1Eout2p3,
				&U2Eout1a,  &U2Eout1p1,  &U2Eout1p2,  &U2Eout1p3,
				&U2Eout2a,  &U2Eout2p1,  &U2Eout2p2,  &U2Eout2p3
			   );
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 1, U1Eout1a, U1Eout1p1, U1Eout1p2, U1Eout1p3, U1Eout2a, U1Eout2p1, U1Eout2p2, U1Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 2, U2Eout1a, U2Eout1p1, U2Eout1p2, U2Eout1p3, U2Eout2a, U2Eout2p1, U2Eout2p2, U2Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 14, GEout1a, GEout1p1, GEout1p2, GEout1p3, GEout2a, GEout2p1, GEout2p2, GEout2p3);
	sleep(10);
	
	// broadcast from 2
	sut_run(0, 0, 1, 2, 
				0, 3, 4, 5, 
				0xF2, 6, 7, 8, 
				&GEout1a,  &GEout1p1,  &GEout1p2,  &GEout1p3,
				&GEout2a,  &GEout2p1,  &GEout2p2,  &GEout2p3,
				&U1Eout1a,  &U1Eout1p1,  &U1Eout1p2,  &U1Eout1p3,
				&U1Eout2a,  &U1Eout2p1,  &U1Eout2p2,  &U1Eout2p3,
				&U2Eout1a,  &U2Eout1p1,  &U2Eout1p2,  &U2Eout1p3,
				&U2Eout2a,  &U2Eout2p1,  &U2Eout2p2,  &U2Eout2p3
			   );
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 1, U1Eout1a, U1Eout1p1, U1Eout1p2, U1Eout1p3, U1Eout2a, U1Eout2p1, U1Eout2p2, U1Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 2, U2Eout1a, U2Eout1p1, U2Eout1p2, U2Eout1p3, U2Eout2a, U2Eout2p1, U2Eout2p2, U2Eout2p3);
	dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 14, GEout1a, GEout1p1, GEout1p2, GEout1p3, GEout2a, GEout2p1, GEout2p2, GEout2p3);
	sleep(10);
	
//	for(int i = 0; i <= 10; i++)
	{
		sut_run(0x1E, 0, 1, 2, 
				0xF1, 3, 4, 5, 
				0xF2, 6, 7, 8, 
				&GEout1a,  &GEout1p1,  &GEout1p2,  &GEout1p3,
				&GEout2a,  &GEout2p1,  &GEout2p2,  &GEout2p3,
				&U1Eout1a,  &U1Eout1p1,  &U1Eout1p2,  &U1Eout1p3,
				&U1Eout2a,  &U1Eout2p1,  &U1Eout2p2,  &U1Eout2p3,
				&U2Eout1a,  &U2Eout1p1,  &U2Eout1p2,  &U2Eout1p3,
				&U2Eout2a,  &U2Eout2p1,  &U2Eout2p2,  &U2Eout2p3
			   );
		dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 1, U1Eout1a, U1Eout1p1, U1Eout1p2, U1Eout1p3, U1Eout2a, U1Eout2p1, U1Eout2p2, U1Eout2p3);
		dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 2, U2Eout1a, U2Eout1p1, U2Eout1p2, U2Eout1p3, U2Eout2a, U2Eout2p1, U2Eout2p2, U2Eout2p3);
		dbg_printf("%15s >>> (Port[0x%x]: [1] addr: 0x%x, payload:%.8f, %.8f, %.8f \n\t\t\t\t\t[2] addr: 0x%x, payload:%.8f, %.8f, %.8f \n)\n", 
				__FUNCTION__, 14, GEout1a, GEout1p1, GEout1p2, GEout1p3, GEout2a, GEout2p1, GEout2p2, GEout2p3);
		sleep(10);
	}
	
	return 0;
}
