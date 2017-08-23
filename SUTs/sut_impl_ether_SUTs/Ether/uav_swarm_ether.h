
#ifndef _UAV_SWARM_CTRL_H_
#define _UAV_SWARM_CTRL_H_

#include "type1.h"
#include "time1.h"

// number of ports connected
#define NUMBER_OF_PORTS 14 

#define PORT_U1 0x1
#define PORT_U2 0x2
#define PORT_GC 0xE

// maximum number of packages got once
#define MAX_PACKAGES (NUMBER_OF_PORTS-1) 

#define SOURCE_ADDR(s) (s & 0x0F)
#define DEST_ADDR(s) ((s & 0xF0) >> 4)

typedef struct {
	int addr;
	double payload[3];
} package_t;

/** Initialize SUT */
void sut_init();

/** Run SUT (one step) */
void sut_run(int GEin1a, double GEin1p1, double GEin1p2, double GEin1p3, 
			int U1Ein1a, double U1Ein1p1, double U1Ein1p2, double U1Ein1p3, 
			int U2Ein1a, double U2Ein1p1, double U2Ein1p2, double U2Ein1p3,
			int* GEout1a, double* GEout1p1, double* GEout1p2, double* GEout1p3,
			int* GEout2a, double* GEout2p1, double* GEout2p2, double* GEout2p3,
			int* U1Eout1a, double* U1Eout1p1, double* U1Eout1p2, double* U1Eout1p3,
			int* U1Eout2a, double* U1Eout2p1, double* U1Eout2p2, double* U1Eout2p3,
			int* U2Eout1a, double* U2Eout1p1, double* U2Eout1p2, double* U2Eout1p3,
			int* U2Eout2a, double* U2Eout2p1, double* U2Eout2p2, double* U2Eout2p3
			);

void ether_run(package_t incoming[NUMBER_OF_PORTS], package_t outgoing[NUMBER_OF_PORTS][MAX_PACKAGES]);

#endif /* _UAV_SWARM_CTRL_H_ */
