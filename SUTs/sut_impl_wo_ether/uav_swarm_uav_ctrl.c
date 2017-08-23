#include "trace.h"
#include "time1.h"
#include "uav_swarm_global_ctrl.h"

static VSTimer_t t[2];

void uav_ctrl_init()
{
	reset(&t[0]);
	reset(&t[1]);
}

static double throttleIpart[2] = {0,0};
static double throttlePpart[2] = {0,0};
static double throttleDpart[2] = {0,0};

static double xIpart[2] = {0,0};
static double xPpart[2] = {0,0};
static double xDpart[2] = {0,0};
static double desiredPitch[2] = {0,0};

static double yIpart[2] = {0,0};
static double yPpart[2] = {0,0};
static double yDpart[2] = {0,0};
static double desiredRoll[2] = {0,0};

const static double THROTTLE_I_CONST = 0.03;
const static double THROTTLE_P_CONST = 1.2;
const static double THROTTLE_D_CONST1 = 1.0;
const static double THROTTLE_D_CONST2 = 0.5;

static void SetThrottle(int index, double targetZ1, double posZ1, double velZ1, double *throttleOut1)
{

	dbg_printf(" %14s >>> throttleIpart:%.8f\n", "", throttleIpart[index]);
	throttleIpart[index] = throttleIpart[index] + ((targetZ1 - posZ1) * THROTTLE_I_CONST);
	throttlePpart[index] = ((targetZ1 - posZ1) * THROTTLE_P_CONST);
	if(velZ1 > 0) 
		throttleDpart[index] = velZ1 * THROTTLE_D_CONST2;
	else
		throttleDpart[index] = velZ1 * THROTTLE_D_CONST1;
	dbg_printf(" %14s <<< throttlePpart:%.8f, throttleIpart:%.8f, throttleDpart:%.8f\n", "", 
			throttlePpart[index], throttleIpart[index], throttleDpart[index]);
	*throttleOut1 = throttleIpart[index] + throttlePpart[index] - throttleDpart[index];
}

const static double PITCH_P_CONST = 0.28;
const static double PITCH_D_CONST = -0.2;
const static double PITCH_MIN_THRESHOLD = -0.35;
const static double PITCH_MAX_THRESHOLD = 0.35;
static void SetPitch(int index, double targetY1, double posY1, double velY1, double *pitchOut1)
{
	dbg_printf(" %14s >>> yIpart:%.8f\n", "", yIpart[index]);
	yIpart[index] = yIpart[index] + ((targetY1 - posY1) * 0);
	yPpart[index] = ((posY1 - targetY1) * PITCH_P_CONST);
	yDpart[index] = velY1 * PITCH_D_CONST;
	desiredPitch[index] = yIpart[index] + yPpart[index] - yDpart[index];
	dbg_printf(" %14s <<< yPpart:%.8f, yIpart:%.8f, yDpart:%.8f, desiredPitch:%.8f\n", "", 
			yPpart[index], yIpart[index], yDpart[index], desiredPitch[index]);
	if(desiredPitch[index] > PITCH_MAX_THRESHOLD) 
		desiredPitch[index] = PITCH_MAX_THRESHOLD; 

	if(desiredPitch[index] < PITCH_MIN_THRESHOLD) 
		desiredPitch[index] = PITCH_MIN_THRESHOLD; 
	*pitchOut1 = desiredPitch[index];
}

const static double ROLL_P_CONST = 0.28;
const static double ROLL_D_CONST = 0.2;
const static double ROLL_MIN_THRESHOLD = -0.35;
const static double ROLL_MAX_THRESHOLD = 0.35;
static void SetRoll(int index, double targetX1, double posX1, double velX1, double *rollOut1)
{
	dbg_printf(" %14s >>> xIpart:%.8f\n", "", xIpart[index]);
	xIpart[index] = xIpart[index] + ((targetX1 - posX1) * 0);
	xPpart[index] = ((targetX1 - posX1) * ROLL_P_CONST);
	xDpart[index] = velX1 * ROLL_D_CONST;
	desiredRoll[index] = xIpart[index] + xPpart[index] - xDpart[index];
	dbg_printf(" %14s <<< xPpart:%.8f, xIpart:%.8f, xDpart:%.8f, desiredRoll:%.8f\n", "", 
			xPpart[index], xIpart[index], xDpart[index], desiredRoll[index]);
	if(desiredRoll[index] > ROLL_MAX_THRESHOLD) 
		desiredRoll[index] = ROLL_MAX_THRESHOLD; 

	if(desiredRoll[index] < ROLL_MIN_THRESHOLD) 
		desiredRoll[index] = ROLL_MIN_THRESHOLD; 
	*rollOut1 = desiredRoll[index];
}

static BOOLEAN firstCall[2] = {1, 1};

// local copy of input variables
static double input[2][10] = {
		{-1,-1,-1,-1,-1,-1,-1,-1,-1,-1}, 
		{-1,-1,-1,-1,-1,-1,-1,-1,-1,-1}
};

// local copy of output variables
static double out[2][4] = {{0, 0, 0, 0}, {0, 0, 0, 0}};

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
	double *yawOut1
	)
{
	BOOLEAN diff = FALSE;

    if(firstCall[index]) 
    {
        if((index == 0 && !elapsed(&t[index], __ms(42))) ||
		   (index == 1 && !elapsed(&t[index], __ms(40))))
        {
			*throttleOut1 = out[index][0];
			*pitchOut1 = out[index][1];
			*rollOut1 = out[index][2];
			*yawOut1 = out[index][3];
            return 0;
        }
    }
    else 
    {
        if(!elapsed(&t[index], __ms(40))) 
        {
			*throttleOut1 = out[index][0];
			*pitchOut1 = out[index][1];
			*rollOut1 = out[index][2];
			*yawOut1 = out[index][3];
            return 0;
        }
    }
    
	if(
		dnequal(targetX1, input[index][0]) ||
		dnequal(targetY1, input[index][1]) ||
		dnequal(targetZ1, input[index][2]) ||
		dnequal(velX1, input[index][3]) ||
		dnequal(velY1, input[index][4]) ||
		dnequal(velZ1, input[index][5]) ||
		dnequal(posX1, input[index][6]) ||
		dnequal(posY1, input[index][7]) ||
		dnequal(posZ1, input[index][8]) ||
		dnequal(batteryCharge, input[index][9])
	)
		diff = TRUE;

	if(diff)
		dbg_printf(
"%15s[%d] >>> (targetX1:%.8f, targetY1:%.8f, targetZ1:%.8f\n \
 %24s      tvelX1:%.8f, velY1:%.8f, velZ1:%.8f\n \
 %24s      posX1:%.8f, posY1:%.8f, posZ1:%.8f\n \
 %24s      batteryCharge:%.8f)\n", 
"[UAV_Ctrl]", index+1, targetX1, targetY1, targetZ1,
"", velX1, velY1, velZ1, 
"", posX1, posY1, posZ1,
"", batteryCharge);
	
	reset(&t[index]);
    firstCall[index] = 0;

	input[index][0] = targetX1;
	input[index][1] = targetY1;
	input[index][2] = targetZ1;
	input[index][3] = velX1;
	input[index][4] = velY1;
	input[index][5] = velZ1;
	input[index][6] = posX1;
	input[index][7] = posY1;
	input[index][8] = posZ1;
	input[index][9] = batteryCharge;
	
	SetThrottle(index, targetZ1, posZ1, velZ1, throttleOut1);
	SetPitch(index, targetY1, posY1, velY1, pitchOut1);
	SetRoll(index, targetX1, posX1, velX1, rollOut1);
	*yawOut1 = 0;
	out[index][0] = *throttleOut1;
	out[index][1] = *pitchOut1;
	out[index][2] = *rollOut1;
	out[index][3] = *yawOut1;

	dbg_printf("%15s[%d] <<< (throttleOut1:%.8f, pitchOut1:%.8f, rollOut1:%.8f, yawOut1:%.8f)\n", "[UAV_Ctrl]",
			index + 1, *throttleOut1, *pitchOut1, *rollOut1, *yawOut1);
	return 1;
}
