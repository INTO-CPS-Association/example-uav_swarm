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

def rm_f(pattern):
    matches = glob.glob(pattern)
    for path in matches:
        try:
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        except OSError as e:
            if os.path.exists(path):
                print("Failed to remove {0}: {1}".format(path, e))
				
def cp_f(source_pattern, target):
    matches = glob.glob(source_pattern)
    for source in matches:
        if os.path.exists(source):
            if os.path.exists(target) and not os.path.isdir(target):
                rm_f(target)
            shutil.copy(source, target)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

## ###################################################################
## EXECUTABLES
## ###################################################################
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

## ###############################################
## [1.1] SUT CREATION: Ether
## ###############################################
def wrap_SUT_ether():
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

	print("## -- Wrapping Ether to FMU --------------------------------------------------")
	os.chdir(os.path.join(context, "sut", "SUTs", "Ether"))
	print("## Compiling sample Ether implementation in '{0}'".format(os.getcwd()))
	if 0 != os.system(" ".join([PROG_make,"all"])):
		raise NameError("Make Failed!")
	print("## Creating RTT_TestProcedures/Ether as wrapper to the modelDescription.xml that fits to SUT : '{0}'".format(os.getcwd()))
	os.chdir(context)

	ether_tpdir = os.path.join(context, "RTT_TestProcedures","Ether")
	print("## Remove {0}".format(ether_tpdir))
	rm_f(ether_tpdir)
	
	print("## Copying modified interface to RTT_TestProcedures/Ether/fmi and inc")
	fmidir = os.path.join(context, "RTT_TestProcedures","Ether","fmi")
	sim_fmidir = os.path.join(context, "RTT_TestProcedures","Simulation", "fmi")
#	mkdir_p(fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.c"), fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.h"), fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.rts"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "Ether", "fmi", "fmi*"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "Ether", "fmi", "Makefile"), fmidir)
	
	ether_tp_incdir = os.path.join(ether_tpdir, "inc")
#	mkdir_p(ether_tp_incdir)
#	cp_f(os.path.join(context, "sut", "SUTs", "Ether", "fmi", "rtt*"), ether_tp_incdir)
	
	if not py(" ".join([PROG_wrap, "--model-description", os.path.join(context, "sut", "SUTs", "Ether", "Ether_modelDescription.xml"), "RTT_TestProcedures/Ether"])):
                sys.stderr.write("Wrapping of Ether failed!\n")
		raise NameError("Wrapping of Ether failed".format(id))
	
	print("## -- Modifying test procedure...")
	append_to_file("""
// -- Added for Ether inclusion -----
CFLAGS	; -I$(RTT_TESTCONTEXT)/sut/SUTs/Ether
CFLAGS	; -DRTT_BLOCK_SIGNAL_SOCKET
INCLUDE ; uav_swarm_ether.h
LDPATH	; -L$(RTT_TESTCONTEXT)/sut/SUTs/Ether 
LDFLAGS ; -luav_swarm_ether 
LDFLAGS ; -DRTT_DEBUG_ENGINE_INTERNAL -DRTT_DEBUG_ENGINE_CALLS -DRTT_FMI_INCLUDE_GET_MAX_STEPSIZE -DRTT_DEBUG_ENGINE_SHM

// --------------------------------
""", os.path.join(context, "RTT_TestProcedures", "Ether", "conf", "swi.conf"))
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
		int    GEin1a;
		double GEin1p1;
		double GEin1p2;
		double GEin1p3;
		int    U1Ein1a;
		double U1Ein1p1;
		double U1Ein1p2;
		double U1Ein1p3;
		int    U2Ein1a;
		double U2Ein1p1;
		double U2Ein1p2;
		double U2Ein1p3;
		// outputs
		int    GEout1a;
		double GEout1p1;
		double GEout1p2;
		double GEout1p3;
		int	   GEout2a;
		double GEout2p1;
		double GEout2p2;
		double GEout2p3;
		int    U1Eout1a;
		double U1Eout1p1;
		double U1Eout1p2;
		double U1Eout1p3;
		int	   U1Eout2a;
		double U1Eout2p1;
		double U1Eout2p2;
		double U1Eout2p3;
		int    U2Eout1a;
		double U2Eout1p1;
		double U2Eout1p2;
		double U2Eout1p3;
		int	   U2Eout2a;
		double U2Eout2p1;
		double U2Eout2p2;
		double U2Eout2p3;


		fprintf(stderr, "STARTING SUT PROCESS\\n");

		while(@rttIsRunning){
			/* Map FMU input variables to SUT: X = rttIOPre->X */
			GEin1a = rttIOPre->GEin1a;
		    GEin1p1 = rttIOPre->GEin1p1;
		    GEin1p2 = rttIOPre->GEin1p2;
		    GEin1p3 = rttIOPre->GEin1p3;
		    U1Ein1a = rttIOPre->U1Ein1a;
		    U1Ein1p1 = rttIOPre->U1Ein1p1;
		    U1Ein1p2 = rttIOPre->U1Ein1p2;
		    U1Ein1p3 = rttIOPre->U1Ein1p3;
		    U2Ein1a = rttIOPre->U2Ein1a;
		    U2Ein1p1 = rttIOPre->U2Ein1p1;
		    U2Ein1p2 = rttIOPre->U2Ein1p2;
		    U2Ein1p3 = rttIOPre->U2Ein1p3;

			sut_run(GEin1a, GEin1p1, GEin1p2, GEin1p3, 
				U1Ein1a, U1Ein1p1, U1Ein1p2, U1Ein1p3, 
				U2Ein1a, U2Ein1p1, U2Ein1p2, U2Ein1p3,
			    &GEout1a, &GEout1p1, &GEout1p2, &GEout1p3,
			    &GEout2a, &GEout2p1, &GEout2p2, &GEout2p3,
			    &U1Eout1a, &U1Eout1p1, &U1Eout1p2, &U1Eout1p3,
			    &U1Eout2a, &U1Eout2p1, &U1Eout2p2, &U1Eout2p3,
			    &U2Eout1a, &U2Eout1p1, &U2Eout1p2, &U2Eout1p3,
			    &U2Eout2a, &U2Eout2p1, &U2Eout2p2, &U2Eout2p3);

			/* Map SUT output to FMU output: rttIOPost->X = X */
			rttIOPost-> GEout1a = GEout1a;
			rttIOPost-> GEout1p1 = GEout1p1;
			rttIOPost-> GEout1p2 = GEout1p2;
			rttIOPost-> GEout1p3 = GEout1p3;
			rttIOPost-> GEout2a = GEout2a;
			rttIOPost-> GEout2p1 = GEout2p1;
			rttIOPost-> GEout2p2 = GEout2p2;
			rttIOPost-> GEout2p3 = GEout2p3;
			rttIOPost-> U1Eout1a = U1Eout1a;
			rttIOPost-> U1Eout1p1 = U1Eout1p1;
			rttIOPost-> U1Eout1p2 = U1Eout1p2;
			rttIOPost-> U1Eout1p3 = U1Eout1p3;
			rttIOPost-> U1Eout2a = U1Eout2a;
			rttIOPost-> U1Eout2p1 = U1Eout2p1;
			rttIOPost-> U1Eout2p2 = U1Eout2p2;
			rttIOPost-> U1Eout2p3 = U1Eout2p3;
			rttIOPost-> U2Eout1a = U2Eout1a;
			rttIOPost-> U2Eout1p1 = U2Eout1p1;
			rttIOPost-> U2Eout1p2 = U2Eout1p2;
			rttIOPost-> U2Eout1p3 = U2Eout1p3;
			rttIOPost-> U2Eout2a = U2Eout2a;
			rttIOPost-> U2Eout2p1 = U2Eout2p1;
			rttIOPost-> U2Eout2p2 = U2Eout2p2;
			rttIOPost-> U2Eout2p3 = U2Eout2p3;

			@rttWaitSilent(1 _ms);
		}
	}
}
int ti_gettimeofday(struct timeval *tv, struct timezone *tz){
	tv->tv_sec	= @t / 1000;		  
	tv->tv_usec = (@t % 1000) * 1000;
	return 0; 
}
""", os.path.join(context, "RTT_TestProcedures", "Ether", "specs", "fmi2sut.rts"))

	print("## Copying modified interface to RTT_TestProcedures/Ether/fmi and inc again to make sure wrapper won't override them")
#	cp_f(os.path.join(context, "sut", "SUTs", "Ether", "fmi", "fmi*"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "Ether", "fmi", "Makefile"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "Ether", "fmi", "rtt*"), ether_tp_incdir)
	
	print("## Building Executable")
	if not py(" ".join([PROG_build, "RTT_TestProcedures/Ether"])):
		raise NameError("Building of Ether failed")

	print "Success: RTT_TestProcedures/Ether can now be used as FMU"

## ###############################################
## [1.2] SUT CREATION: Global Controller
## ###############################################
def wrap_SUT_globalctrl():
	print("## -- Wrapping Global Controller to FMU --------------------------------------------------")
	os.chdir(os.path.join(context, "sut", "SUTs", "GlobalCtrl"))
	print("## Compiling sample GlobalCtrl implementation in '{0}'".format(os.getcwd()))
	if 0 != os.system(" ".join([PROG_make,"all"])):
		raise NameError("Make Failed!")
	print("## Creating RTT_TestProcedures/GlobalCtrl as wrapper to the modelDescription.xml that fits to SUT : '{0}'".format(os.getcwd()))
	os.chdir(context)

	tpdir = os.path.join(context, "RTT_TestProcedures","GlobalCtrl")
	print("## Remove {0}".format(tpdir))
	rm_f(tpdir)
	
#	print("## Copying modified interface to RTT_TestProcedures/GlobalCtrl/fmi and inc")
#	fmidir = os.path.join(context, "RTT_TestProcedures","GlobalCtrl","fmi")
#	sim_fmidir = os.path.join(context, "RTT_TestProcedures","Simulation", "fmi")
#	mkdir_p(fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.c"), fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.h"), fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.rts"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "GlobalCtrl", "fmi", "fmi*"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "GlobalCtrl", "fmi", "Makefile"), fmidir)
#	
#	tp_incdir = os.path.join(tpdir, "inc")
#	mkdir_p(tp_incdir)
#	cp_f(os.path.join(context, "sut", "SUTs", "GlobalCtrl", "fmi", "rtt*"), tp_incdir)
	
	if not py(" ".join([PROG_wrap, "--model-description", os.path.join(context, "sut", "SUTs", "GlobalCtrl", "GlobalCtrl_modelDescription.xml"), "RTT_TestProcedures/GlobalCtrl"])):
                sys.stderr.write("Wrapping of GlobalCtrl failed!\n")
		raise NameError("Wrapping of GlobalCtrl failed")
	
	print("## -- Modifying test procedure...")
	append_to_file("""
// -- Added for Ether inclusion -----
CFLAGS	; -I$(RTT_TESTCONTEXT)/sut/SUTs/GlobalCtrl
CFLAGS	; -DRTT_BLOCK_SIGNAL_SOCKET
INCLUDE ; uav_swarm_globalctrl.h
LDPATH	; -L$(RTT_TESTCONTEXT)/sut/SUTs/GlobalCtrl 
LDFLAGS ; -luav_swarm_globalctrl  
LDFLAGS ; -DRTT_DEBUG_ENGINE_INTERNAL -DRTT_DEBUG_ENGINE_CALLS -DRTT_FMI_INCLUDE_GET_MAX_STEPSIZE -DRTT_DEBUG_ENGINE_SHM
// --------------------------------
""", os.path.join(context, "RTT_TestProcedures", "GlobalCtrl", "conf", "swi.conf"))
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
		double targetX2;
		double targetY2;
		double targetZ2;
		
		int    GEout1a;
		double GEout1p1;
		double GEout1p2;
		double GEout1p3;
		int	   GEout2a;
		double GEout2p1;
		double GEout2p2;
		double GEout2p3;
		
		// outputs
		int    GEin1a;
		double GEin1p1;
		double GEin1p2;
		double GEin1p3;

		fprintf(stderr, "STARTING Global Controller PROCESS\\n");

		while(@rttIsRunning){
			/* Map FMU input variables to SUT: X = rttIOPre->X */
			targetX1 = rttIOPre -> targetX1;
			targetY1 = rttIOPre -> targetY1;
			targetZ1 = rttIOPre -> targetZ1;
			targetX2 = rttIOPre -> targetX2;
			targetY2 = rttIOPre -> targetY2;
			targetZ2 = rttIOPre -> targetZ2;
			GEout1a = rttIOPre -> GEout1a;
			GEout1p1 = rttIOPre -> GEout1p1;
			GEout1p2 = rttIOPre -> GEout1p2;
			GEout1p3 = rttIOPre -> GEout1p3;
			GEout2a = rttIOPre -> GEout2a;
			GEout2p1 = rttIOPre -> GEout2p1;
			GEout2p2 = rttIOPre -> GEout2p2;
			GEout2p3 = rttIOPre -> GEout2p3;

			sut_run(targetX1, targetY1, targetZ1, 
				targetX2, targetY2, targetZ2, 
				GEout1a, GEout1p1, GEout1p2, GEout1p3, 
				GEout2a, GEout2p1, GEout2p2, GEout2p3, 
			    &GEin1a, &GEin1p1, &GEin1p2, &GEin1p3);

			/* Map SUT output to FMU output: rttIOPost->X = X */
			rttIOPost-> GEin1a = GEin1a;
			rttIOPost-> GEin1p1 = GEin1p1 ;
			rttIOPost-> GEin1p2 = GEin1p2;
			rttIOPost-> GEin1p3 = GEin1p3;

			@rttWaitSilent(1 _ms);
		}
	}
}
int ti_gettimeofday(struct timeval *tv, struct timezone *tz){
	tv->tv_sec	= @t / 1000;		  
	tv->tv_usec = (@t % 1000) * 1000;
	return 0; 
}
""", os.path.join(context, "RTT_TestProcedures", "GlobalCtrl", "specs", "fmi2sut.rts"))

#	print("## Copying modified interface to RTT_TestProcedures/GlobalCtrl/fmi and inc again to make sure wrapper won't override them")
#	cp_f(os.path.join(context, "sut", "SUTs", "GlobalCtrl", "fmi", "fmi*"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "GlobalCtrl", "fmi", "Makefile"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "GlobalCtrl", "fmi", "rtt*"), tp_incdir)
	
	print("## Building Executable")
	if not py(" ".join([PROG_build, "RTT_TestProcedures/GlobalCtrl"])):
		raise NameError("Building of GlobalCtrl failed")

	print "Success: RTT_TestProcedures/GlobalCtrl can now be used as FMU"
	
## ###############################################
## [1.2] SUT CREATION: UAV Controller
## ###############################################
def wrap_SUT_uavctrl(id):
	print """
======================================================================
=== attempting creation of RTT_Testprocedures/UAVCtrl{id}
======================================================================
""".format(id=id)

	print("## -- Wrapping UAV Controller to FMU:  --------------------------------------------------")
	os.chdir(os.path.join(context, "sut", "SUTs", "UAVCtrl"))
	print("## Compiling sample UAVCtrl implementation in '{0}'".format(os.getcwd()))
	if 0 != os.system(" ".join([PROG_make,"all"])):
		raise NameError("Make Failed!")
	print("## Creating RTT_TestProcedures/UAVCtrl as wrapper to the modelDescription.xml that fits to SUT : '{0}'".format(os.getcwd()))
	os.chdir(context)
	
	tpdir = os.path.join(context, "RTT_TestProcedures","UAVCtrl{id}".format(id=id))
	print("## Remove {0}".format(tpdir))
	rm_f(tpdir)
	
#	print("## Copying modified interface to RTT_TestProcedures/UAVCtrl/fmi and inc")
#	fmidir = os.path.join(context, "RTT_TestProcedures","UAVCtrl{id}".format(id=id),"fmi")
#	sim_fmidir = os.path.join(context, "RTT_TestProcedures","Simulation", "fmi")
#	mkdir_p(fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.c"), fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.h"), fmidir)
#	cp_f(os.path.join(sim_fmidir, "*.rts"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "UAVCtrl", "fmi", "fmi*"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "UAVCtrl", "fmi", "Makefile"), fmidir)
#	
#	tp_incdir = os.path.join(tpdir, "inc")
#	mkdir_p(tp_incdir)
#	cp_f(os.path.join(context, "sut", "SUTs", "UAVCtrl", "fmi", "rtt*"), tp_incdir)
	
	if not py(" ".join([PROG_wrap, "--model-description", os.path.join(context, "sut", "SUTs", "UAVCtrl", "UAVCtrl_modelDescription.xml"), "RTT_TestProcedures/UAVCtrl{id}".format(id=id)])):
                sys.stderr.write("Wrapping of UAVCtrl{id} failed!\n".format(id=id))
		raise NameError("Wrapping of UAVCtrl failed")
	
	print("## -- Modifying test procedure...")
	append_to_file("""
// -- Added for UAVCtrl inclusion -----
CFLAGS	; -I$(RTT_TESTCONTEXT)/sut/SUTs/UAVCtrl
CFLAGS	; -DRTT_BLOCK_SIGNAL_SOCKET
INCLUDE ; uav_swarm_uavctrl.h
LDPATH	; -L$(RTT_TESTCONTEXT)/sut/SUTs/UAVCtrl 
LDFLAGS ; -luav_swarm_uavctrl  
LDFLAGS ; -DRTT_DEBUG_ENGINE_INTERNAL -DRTT_DEBUG_ENGINE_CALLS -DRTT_FMI_INCLUDE_GET_MAX_STEPSIZE -DRTT_DEBUG_ENGINE_SHM
// --------------------------------
""", os.path.join(context, "RTT_TestProcedures", "UAVCtrl{id}".format(id=id), "conf", "swi.conf"))
	am_def = """
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
		double velX;
		double velY;
		double velZ;
		double posX;
		double posY;
		double posZ;
		double battery = 0;
		
		int    UAVout1a;
		double UAVout1p1;
		double UAVout1p2;
		double UAVout1p3;
		int	   UAVout2a;
		double UAVout2p1;
		double UAVout2p2;
		double UAVout2p3;
		
		// outputs
		int    UAVin1a;
		double UAVin1p1;
		double UAVin1p2;
		double UAVin1p3;
		double throttleOut;
		double pitchOut;
		double rollOut;
		double yawOut;

		fprintf(stderr, "STARTING UAV Controller PROCESS\\n");

		while(@rttIsRunning){
			/* Map FMU input variables to SUT: X = rttIOPre->X */
			velX = rttIOPre -> velX;
			velY = rttIOPre -> velY;
			velZ = rttIOPre -> velZ;
			posX = rttIOPre -> posX;
			posY = rttIOPre -> posY;
			posZ = rttIOPre -> posZ;
			UAVout1a = rttIOPre -> UAVout1a;
			UAVout1p1 = rttIOPre -> UAVout1p1;
			UAVout1p2 = rttIOPre -> UAVout1p2;
			UAVout1p3 = rttIOPre -> UAVout1p3;
			UAVout2a = rttIOPre -> UAVout2a;
			UAVout2p1 = rttIOPre -> UAVout2p1;
			UAVout2p2 = rttIOPre -> UAVout2p2;
			UAVout2p3 = rttIOPre -> UAVout2p3;

			sut_run(@ID@, velX, velY, velZ, 
				posX, posY, posZ, battery,
				UAVout1a, UAVout1p1, UAVout1p2, UAVout1p3, 
				UAVout2a, UAVout2p1, UAVout2p2, UAVout2p3, 
			    &UAVin1a, &UAVin1p1, &UAVin1p2, &UAVin1p3,
				&throttleOut, &pitchOut, &rollOut, &yawOut);

			/* Map SUT output to FMU output: rttIOPost->X = X */
			rttIOPost-> UAVin1a = UAVin1a;
			rttIOPost-> UAVin1p1 = UAVin1p1 ;
			rttIOPost-> UAVin1p2 = UAVin1p2;
			rttIOPost-> UAVin1p3 = UAVin1p3;
			rttIOPost-> throttleOut = throttleOut;
			rttIOPost-> pitchOut = pitchOut ;
			rttIOPost-> rollOut = rollOut;
			rttIOPost-> yawOut = yawOut;

			@rttWaitSilent(1 _ms);
		}
	}
}
int ti_gettimeofday(struct timeval *tv, struct timezone *tz){
	tv->tv_sec	= @t / 1000;		  
	tv->tv_usec = (@t % 1000) * 1000;
	return 0; 
}
"""

	define_sut_in_rts(am_def.replace("@ID@", id), os.path.join(context, "RTT_TestProcedures", "UAVCtrl{id}".format(id=id), "specs", "fmi2sut.rts"))

#	print("## Copying modified interface to RTT_TestProcedures/UAVCtrl/fmi and inc again to make sure wrapper won't override them")
#	cp_f(os.path.join(context, "sut", "SUTs", "UAVCtrl", "fmi", "fmi*"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "UAVCtrl", "fmi", "Makefile"), fmidir)
#	cp_f(os.path.join(context, "sut", "SUTs", "UAVCtrl", "fmi", "rtt*"), tp_incdir)
	
	print("## Building Executable")
	if not py(" ".join([PROG_build, "RTT_TestProcedures/UAVCtrl{id}".format(id=id)])):
		raise NameError("Building of UAVCtrl{id} failed".format(id=id))

	print "Success: RTT_TestProcedures/UAVCtrl{id} can now be used as FMU".format(id=id)
	
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

try:
	print("## -- Building Ether ---------------------------------------------------------")
	print("## -- Backup specs/fmi2rttInterface.rts -----------------------------------")
	shutil.copyfile(os.path.join(context,"specs","fmi2rttInterface.rts"), os.path.join(context,"specs","fmi2rttInterface.rts.tp00"))

	print("## -- Wrapping SUTs to FMUs --------------------------------------------------")
	os.chdir(context)
	wrap_SUT_ether()
	wrap_SUT_globalctrl()
	wrap_SUT_uavctrl("1")
	wrap_SUT_uavctrl("2")

	py(os.path.join(context, "sut", "assembly_json_for_test.py"))
except:
	print "!! "
	print "!! Creating of SUT-FMU failed, use 'Simulation' for your experiments."
	print "!! "

print("## -- Restore specs/fmi2rttInterface.rts -----------------------------------")
shutil.move(os.path.join(context,"specs","fmi2rttInterface.rts.tp00"), os.path.join(context,"specs","fmi2rttInterface.rts"))

print """
----------------------------------------------------------------------
   Project Initialisation Finished: uav_swarm_ether 
----------------------------------------------------------------------
"""

