#! /usr/bin/env python
# This script initialises the 'fcu_rtt_mbt/SUT' in RTT_TestProcedure 
# It is copied from the water_tank.v2 in VSI_Bundle.exe

import os
import glob
import sys
#import xml.etree.ElementTree as ET
import json
import httplib
# for file copy
import shutil
from optparse import OptionParser

import datetime

global opt_VERBOSE
opt_VERBOSE = ["--verbose"]

## ###################################################################
## AUX FUNCTIONS
## ###################################################################

def is_exe(fpath):
	return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def get_exe(fpath):
	if is_exe(fpath):
		return fpath
	if "PATHEXT" in os.environ:
		for extension in os.environ["PATHEXT"].split(";"):
			newfpath = fpath + extension.lower()
			if is_exe(newfpath):
				return newfpath
	return None

def which(program):
	import os

	fpath, fname = os.path.split(program)
	if fpath:
		fpathext = get_exe(program)
		if fpathext is not None:
			return fpathext
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"')
			exe_file = os.path.join(path, program)
			exe_file_ext = get_exe(exe_file)
			if exe_file_ext is not None:
				return exe_file_ext
	pass

def py(scriptcall):
	blurt("Invoking [" + sys.platform + "] " + scriptcall)
	if sys.platform.startswith('win'):
		ret = os.system("C:\\Python27\\python.exe" + " " + scriptcall)
	else:
		ret = os.system(scriptcall)
	return (0 == ret)

def is_empty(any_structure):
	if any_structure:
		return False
	else:
		return True

def blurt(s):
	if not is_empty(opt_VERBOSE):
		sys.stderr.write(s + '\n')

def append_to_file(string, file):
	"""Append a (possible multi-line) string to an existing file.
	Fails if the file does not exist.
	"""
	if not os.path.isfile(file):
		sys.stderr.write("ERROR: append_to_file(): file '{0}' does not exist.\n".format(file))
		raise NameError("File does not exist")
	print("# -> appending to " + file)
	with open(file, "a") as out:
			out.write(string)

def define_sut_in_rts(string, file):
	"""In an existing rts-file, replace everything from 
		 '@abstract machine sut()'
	onward by the string.
	Fails if the file does not exist.
	"""
	if not os.path.isfile(file):
		sys.stderr.write("ERROR: append_to_file(): file '{0}' does not exist.\n".format(file))
		raise NameError("File does not exist")
	bak = file + ".BAK"
	print("# -> changing AM SUT in " + file)
	try:
		os.remove(bak)
	except:
		pass
	os.rename(file, bak)
	with open(bak, "r") as old_file:
		with open(file, "w") as out:
			for line in old_file:
				if line.startswith('@abstract machine sut()'):
					out.write(string)
					return
				else:
					out.write(line)

## ###################################################################
## MAIN
## ###################################################################

usage = """init-prj.py

Project-specific intialisation that build most relevant files, starting
with model import.

"""
__version__ = "$Revision: 1.1.2.5 $".replace("$", "")

parser = OptionParser(usage=usage, version=__version__)
(options, args) = parser.parse_args()


if len(args) != 0:
	sys.stderr.write("ERROR: init-prj.py: surplus number of arguments\n")
	print usage
	sys.exit(0)

context = os.path.realpath(os.path.join(os.path.realpath(__file__), "..", "..", ".."))

os.environ['RTT_TESTCONTEXT'] = context

print "Using RTT_TESTCONTEXT=" + context

if sys.platform.startswith('win'):
	os.environ["PATH"] = os.pathsep.join([os.path.join(os.environ["RTTDIR"], "bin"), os.environ["PATH"], "C:\\opt\\gcc-4.9-win64\\bin"])
	PROG_make = "make.exe"
	MBTDIR="C:\\opt\\rtt-mbt"
	RTTDIR="C:\\opt\\rt-tester"
else:
	PROG_make = which("make")
	MBTDIR="/opt/rtt-mbt"
	RTTDIR="/opt/rt-tester"

PROG_init  = os.path.join(MBTDIR, "bin", "rtt-mbt-init-project.py")
PROG_wrap  = os.path.join(MBTDIR, "bin", "rtt-mbt-fmi2-wrap-to-fmu.py")
PROG_sim   = os.path.join(MBTDIR, "bin", "rtt-mbt-fmi2gen-sim.py")
PROG_tp	   = os.path.join(MBTDIR, "bin", "rtt-mbt-fmi2gen.py")
PROG_solve = os.path.join(MBTDIR, "bin", "rtt-mbt-gen.py")
PROG_build = os.path.join(RTTDIR, "bin", "rtt-build-test.py")

#print("## -- Importing model ------------------------------------------------------")
#py(" ".join([PROG_init, os.path.join(context, "model", "water-tank.xmi")]))

#print("## -- Creating Simulation -------------------------------------------------")
#py(" ".join([PROG_sim, "TestProcedures/Simulation"]))

# print("## -- Creating Test TP-BCS ------------------------------------------------")
# if py(" ".join([PROG_solve, "TestProcedures/TP-BCS"])):
#	  py(" ".join([PROG_tp, "RTT_TestProcedures/TP-BCS"]))

#print("## -- Creating Test TP-TR -------------------------------------------------")
#if py(" ".join([PROG_solve, "TestProcedures/TP-TR"])):
#	py(" ".join([PROG_tp, "RTT_TestProcedures/TP-TR"]))

print("## -- Building SUT ---------------------------------------------------------")
try:
	print("## -- Backup specs/fmi2rttInterface.rts -----------------------------------")
	shutil.copyfile(os.path.join(context,"specs","fmi2rttInterface.rts"), os.path.join(context,"specs","fmi2rttInterface.rts.tp00"))

	print("## -- Wrapping SUT to FMU --------------------------------------------------")
	os.chdir(os.path.join(context, "sut", "SUT"))
	print("## Compiling sample SUT implementation in '{0}'".format(os.getcwd()))
	if 0 != os.system(" ".join([PROG_make,"all"])):
		raise NameError("Make Failed!")
	print("## Creating RTT_TestProcedures/SUT as wrapper to the modelDescription.xml that fits to SUT".format(os.getcwd()))
	os.chdir(context)
	if not py(" ".join([PROG_wrap, "--model-description", os.path.join(context, "RTT_TestProcedures", "Simulation", "model", "modelDescription.xml"), "RTT_TestProcedures/SUT"])):
		raise NameError("Wrapping of SUT failed")
	print("## -- Modifying test procedure...")
	append_to_file("""
// -- Added for SUT inclusion -----
CFLAGS	; -I$(RTT_TESTCONTEXT)/sut/SUT
INCLUDE ; uav_swarm_ctrl.h
LDPATH	; -L$(RTT_TESTCONTEXT)/sut/SUT
LDFLAGS ; -luav_swarm_ctrl
// --------------------------------
""", os.path.join(context, "RTT_TestProcedures", "SUT", "conf", "swi.conf"))
	define_sut_in_rts("""
@abstract machine sut()
{					   
	@INIT:{			   
		fprintf(stderr, "CALL SUT INIT\\n");
		sut_init();						   
	}									   
	@FINIT:{							   
		//
	}
	@PROCESS:{
		double targetX1;
		double targetY1;
		double targetZ1;
		double posX1;
		double posY1;
		double posZ1;
		double velX1;
		double velY1;
		double velZ1;
		double batteryCharge1;
		double targetX2;
		double targetY2;
		double targetZ2;
		double posX2;
		double posY2;
		double posZ2;
		double velX2;
		double velY2;
		double velZ2;
		double batteryCharge2;
		// outputs
		double throttleOut1;
		double pitchOut1;
		double rollOut1;
		double yawOut1;
		double throttleOut2;
		double pitchOut2;
		double rollOut2;
		double yawOut2;


		fprintf(stderr, "STARTING SUT PROCESS\\n");

		while(@rttIsRunning){
			/* Map FMU input variables to SUT: X = rttIOPre->X */
			targetX1 = rttIOPre->targetX1;
			targetY1 = rttIOPre->targetY1;
			targetZ1 = rttIOPre->targetZ1;
			posX1 = rttIOPre->posX1;
			posY1 = rttIOPre->posY1;
			posZ1 = rttIOPre->posZ1;
			velX1 = rttIOPre->velX1;
			velY1 = rttIOPre->velY1;
			velZ1 = rttIOPre->velZ1;
			batteryCharge1 = rttIOPre->batteryCharge1;
			targetX2 = rttIOPre->targetX2;
			targetY2 = rttIOPre->targetY2;
			targetZ2 = rttIOPre->targetZ2;
			posX2 = rttIOPre->posX2;
			posY2 = rttIOPre->posY2;
			posZ2 = rttIOPre->posZ2;
			velX2 = rttIOPre->velX2;
			velY2 = rttIOPre->velY2;
			velZ2 = rttIOPre->velZ2;
			batteryCharge2 = rttIOPre->batteryCharge2;

			sut_run(targetX1, targetY1, targetZ1, velX1, velY1, velZ1,
					posX1, posY1, posZ1, batteryCharge1, 
					targetX2, targetY2, targetZ2, velX2, velY2, velZ2,
					posX2, posY2, posZ2, batteryCharge2, 
					&throttleOut1, &pitchOut1, &rollOut1, &yawOut1,
					&throttleOut2, &pitchOut2, &rollOut2, &yawOut2);

			/* Map SUT output to FMU output: rttIOPost->X = X */
			rttIOPost->throttleOut1 = throttleOut1;
			rttIOPost->pitchOut1 = pitchOut1;
			rttIOPost->rollOut1 = rollOut1;
			rttIOPost->yawOut1 = yawOut1;
			rttIOPost->throttleOut2 = throttleOut2;
			rttIOPost->pitchOut2 = pitchOut2;
			rttIOPost->rollOut2 = rollOut2;
			rttIOPost->yawOut2 = yawOut2;

			@rttWaitSilent(1 _ms);
		}
	}
}
int ti_gettimeofday(struct timeval *tv, struct timezone *tz){
	tv->tv_sec	= @t / 1000;		  
	tv->tv_usec = (@t % 1000) * 1000;
	return 0; 
}
""", os.path.join(context, "RTT_TestProcedures", "SUT", "specs", "fmi2sut.rts"))
	print("## Building Executable")
	if not py(" ".join([PROG_build, "RTT_TestProcedures/SUT"])):
		raise NameError("Building of SUT failed")

	print "Success: RTT_TestProcedures/SUT can now be used as FMU"

except:
	print "!! "
	print "!! Creating of SUT-FMU failed, use 'Simulation' for your experiments."
	print "!! "

print("## -- Restore specs/fmi2rttInterface.rts -----------------------------------")
shutil.move(os.path.join(context,"specs","fmi2rttInterface.rts.tp00"), os.path.join(context,"specs","fmi2rttInterface.rts"))

print """
----------------------------------------------------------------------
   Project Initialisation Finished: uav_swarm_ctrl 
----------------------------------------------------------------------
"""

