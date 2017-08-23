#include <string.h>
#include "trace.h"
#include "uav_swarm_ether.h"

static VSTimer_t t;

static package_t local_outgoing[NUMBER_OF_PORTS][MAX_PACKAGES];
static void init_outgoing(package_t outgoing[][MAX_PACKAGES])
{
	for(int i = 0; i < NUMBER_OF_PORTS; i++)
		for(int j = 0; j < MAX_PACKAGES; j++)
		{
			outgoing[i][j].addr = 0;
			outgoing[i][j].payload[0] = 0;
			outgoing[i][j].payload[1] = 0;
			outgoing[i][j].payload[2] = 0;
		}
}

static void init_incoming(package_t incoming[])
{
	for(int i = 0; i < NUMBER_OF_PORTS; i++)
	{
		incoming[i].addr = 0;
		incoming[i].payload[0] = 0;
		incoming[i].payload[1] = 0;
		incoming[i].payload[2] = 0;
	}
}

static void copy_package(package_t in, package_t* out)
{
	out->addr = in.addr;
	out->payload[0] = in.payload[0];
	out->payload[1] = in.payload[1];
	out->payload[2] = in.payload[2];
}

/** Initialize SUT */
void sut_init()
{
	dbg_init("sut.log");
	reset(&t);
}

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
			)
{
	package_t incoming[NUMBER_OF_PORTS];
	package_t outgoing[NUMBER_OF_PORTS][MAX_PACKAGES];

	init_incoming(incoming);
	init_outgoing(outgoing);

	// copy input
	incoming[PORT_U1-1].addr = U1Ein1a;
	incoming[PORT_U1-1].payload[0] = U1Ein1p1;
	incoming[PORT_U1-1].payload[1] = U1Ein1p2;
	incoming[PORT_U1-1].payload[2] = U1Ein1p3;
	incoming[PORT_U2-1].addr = U2Ein1a;
	incoming[PORT_U2-1].payload[0] = U2Ein1p1;
	incoming[PORT_U2-1].payload[1] = U2Ein1p2;
	incoming[PORT_U2-1].payload[2] = U2Ein1p3;
	incoming[PORT_GC-1].addr = GEin1a;
	incoming[PORT_GC-1].payload[0] = GEin1p1;
	incoming[PORT_GC-1].payload[1] = GEin1p2;
	incoming[PORT_GC-1].payload[2] = GEin1p3;

	ether_run(incoming, outgoing);

	// copy output
	*U1Eout1a = outgoing[PORT_U1-1][0].addr;
	*U1Eout1p1 = outgoing[PORT_U1-1][0].payload[0];
	*U1Eout1p2 = outgoing[PORT_U1-1][0].payload[1];
	*U1Eout1p3 = outgoing[PORT_U1-1][0].payload[2];
	*U1Eout2a = outgoing[PORT_U1-1][1].addr;
	*U1Eout2p1 = outgoing[PORT_U1-1][1].payload[0];
	*U1Eout2p2 = outgoing[PORT_U1-1][1].payload[1];
	*U1Eout2p3 = outgoing[PORT_U1-1][1].payload[2];
	*U2Eout1a = outgoing[PORT_U2-1][0].addr;
	*U2Eout1p1 = outgoing[PORT_U2-1][0].payload[0];
	*U2Eout1p2 = outgoing[PORT_U2-1][0].payload[1];
	*U2Eout1p3 = outgoing[PORT_U2-1][0].payload[2];
	*U2Eout2a = outgoing[PORT_U2-1][1].addr;
	*U2Eout2p1 = outgoing[PORT_U2-1][1].payload[0];
	*U2Eout2p2 = outgoing[PORT_U2-1][1].payload[1];
	*U2Eout2p3 = outgoing[PORT_U2-1][1].payload[2];
	*GEout1a = outgoing[PORT_GC-1][0].addr;
	*GEout1p1 = outgoing[PORT_GC-1][0].payload[0];
	*GEout1p2 = outgoing[PORT_GC-1][0].payload[1];
	*GEout1p3 = outgoing[PORT_GC-1][0].payload[2];
	*GEout2a = outgoing[PORT_GC-1][1].addr;
	*GEout2p1 = outgoing[PORT_GC-1][1].payload[0];
	*GEout2p2 = outgoing[PORT_GC-1][1].payload[1];
	*GEout2p3 = outgoing[PORT_GC-1][1].payload[2];
}


void ether_run(package_t incoming[], package_t outgoing[][MAX_PACKAGES])
{
	if(!elapsed(&t, __ms(10)))
	{
		memcpy(outgoing, local_outgoing, sizeof(local_outgoing));
		return;
	}

	for(int i = 0; i < NUMBER_OF_PORTS; i++) 
	{
		if(incoming[i].addr != 0) 
		{
			dbg_printf("%15s >>> (Port[0x%x]: addr: 0x%x, payload:%.8f, %.8f, %.8f)\n", 
				__FUNCTION__, i+1, incoming[i].addr, incoming[i].payload[0], incoming[i].payload[1], incoming[i].payload[2] );
		}
	}
	reset(&t);
	
	// We won't override an existing signal in a port if there is no new signal for this port
	// If there is a new package for this port, then it will be overridden. 
	//init_outgoing(outgoing);
	memcpy(outgoing, local_outgoing, sizeof(local_outgoing));

	// the index of current outgoing buffer
	int outgoing_index[NUMBER_OF_PORTS] = {0};
	// the first index 0 is always reserved for the target positions package from GC
	for(int i = 0; i < NUMBER_OF_PORTS; i++) 
	{
		outgoing_index[i] = 1;
	}

	// first time, we check GE port to make sure it is put in the first place of outgoing packages.
	int first = 1;
	
	// for outgoing packages, target positions from GE should be put first, and then it is broadcast packages
	for(int k = 0, i = 0; k < NUMBER_OF_PORTS - 1; k++) 
	{
		if(first == 1) 
		{
			i = NUMBER_OF_PORTS - 1;
			k--; // make k start from 0 again
			first = 0;
		}
		else 
		{
			i = k;
		}

		// check if source address matches with port number
		//	otherwise, do nothing
		if(SOURCE_ADDR(incoming[i].addr) == (i + 1))
		{
			if(DEST_ADDR(incoming[i].addr) == 0xF) 
			{
				// copy packages to other port
				for(int j = 0; j < NUMBER_OF_PORTS; j++) 
				{
					// ignore itself
					if(j != i) 
					{
						copy_package(incoming[i], &outgoing[j][outgoing_index[j]]);
						outgoing_index[j]++;
					}
				}
			}
			else if(DEST_ADDR(incoming[i].addr) == 0)  
			{
				dbg_printf("%15s The destination address (0x%x) of incoming package of Port[%d] shouldn't be 0\n", 
					__FUNCTION__, incoming[i].addr, i+1);
			}
			else 
			{
				if(i == NUMBER_OF_PORTS - 1) 
				{
					// package from GC, then copy to the first place of outgoing packages
					// copy to the destination port
					int kk = DEST_ADDR(incoming[i].addr);
					copy_package(incoming[i], &outgoing[kk-1][0]);
					dbg_printf("%15s Copy a package from Port[%d] (0x%x, %.8f, %.8f, %.8f) to Port[%d] ([%d]) \n", 
						__FUNCTION__, i+1, incoming[i].addr, incoming[i].payload[0], incoming[i].payload[1], incoming[i].payload[2],
						kk, 0);
				}
				else 
				{
					// copy to the destination port
					int kk = DEST_ADDR(incoming[i].addr);
					copy_package(incoming[i], &outgoing[kk-1][outgoing_index[kk-1]]);
					dbg_printf("%15s Copy a package from Port[%d] (0x%x, %.8f, %.8f, %.8f) to Port[%d] ([%d]) \n", 
						__FUNCTION__, i+1, incoming[i].addr, incoming[i].payload[0], incoming[i].payload[1], incoming[i].payload[2],
						kk, outgoing_index[kk-1]);

					outgoing_index[kk-1]++;
				}
			}
		} 
		else if(SOURCE_ADDR(incoming[i].addr) == (i + 1))
		{ // ignore
		}
		else
		{
			if(incoming[i].addr != 0)
				dbg_printf("%15s The address (0x%x) of incoming package of Port[%d] doesn't match its port address (0x%x)\n", 
					__FUNCTION__, incoming[i].addr, i+1, i+1);
		}
	}

	memcpy(local_outgoing, outgoing, sizeof(local_outgoing));

	for(int i = 0; i < NUMBER_OF_PORTS; i++) 
		for(int j = 0; j < MAX_PACKAGES; j++) 
		{
			if(outgoing[i][j].addr != 0) 
			{
				dbg_printf("%15s <<< (Port[%d][%d]: addr: 0x%x, payload:%.8f, %.8f, %.8f)\n", 
					__FUNCTION__, i+1, j+1, outgoing[i][j].addr, outgoing[i][j].payload[0], outgoing[i][j].payload[1], outgoing[i][j].payload[2] );
			}
		}
}
