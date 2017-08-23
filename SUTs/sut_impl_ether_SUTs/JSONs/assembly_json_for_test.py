#! /usr/bin/env python
# This script updates the GUIDs in SUT_roomwall.json according to its current GUIDs. 

import os
import glob
import sys
import xml.etree.ElementTree as ET
import json
import httplib
import zipfile
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

def get_guid(filename):
	print "Filename: " + filename
	if is_exe(filename):
		pass
	else:
		print "File {0} doesn't exist!".format(filename)
		raise
		
	try: 
		with zipfile.ZipFile(filename, 'r') as zip:
			print "Scanning file " + filename
			modelDescritionXML = zip.read("modelDescription.xml")
			rootNode = ET.fromstring(modelDescritionXML)			
			guid = rootNode.get("guid")

			print "guid = " + guid
			return guid
	except zipfile.BadZipfile: 
		print "Bad Zip file: {0}".format(filename)
	except Exception,err: 
		print "Failed to open file: {0}, and err: {1}".format(filename, str(err))
		
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

## ###################################################################
## MAIN
## ###################################################################

usage = """assembly_json_for_test.py

This script updates the GUIDs in SUT_roomwall.json according to its current GUIDs. 

"""
__version__ = "$Revision: 0.0.1.0 $".replace("$", "")

parser = OptionParser(usage=usage, version=__version__)
(options, args) = parser.parse_args()


if len(args) != 0:
	sys.stderr.write("ERROR: assembly_json_for_test.py: surplus number of arguments\n")
	print usage
	sys.exit(0)

context = os.path.realpath(os.path.join(os.path.realpath(__file__), "..", ".."))

os.environ['RTT_TESTCONTEXT'] = context

print "Using RTT_TESTCONTEXT=" + context

try:
	print("## -- Get GUID for TP4SUT_UAVSwarm -----------------------------------------------")
	tpFmuPath = os.path.join(context,"RTT_TestProcedures","TP-00", "INTO-CPS-Demo.fmu")
	etherFmuPath = os.path.join(context,"RTT_TestProcedures","Ether", "INTO-CPS-Demo_sut.fmu")
	gcFmuPath = os.path.join(context,"RTT_TestProcedures","GlobalCtrl", "INTO-CPS-Demo_sut.fmu")
	uavctrl1FmuPath = os.path.join(context,"RTT_TestProcedures","UAVCtrl1", "INTO-CPS-Demo_sut.fmu")
	uavctrl2FmuPath = os.path.join(context,"RTT_TestProcedures","UAVCtrl2", "INTO-CPS-Demo_sut.fmu")
	uav1FmuPath = os.path.join(context,"RTT_TestProcedures","UAV1", "UAV.fmu")
	uav2FmuPath = os.path.join(context,"RTT_TestProcedures","UAV2", "UAV.fmu")
	tpGuid = get_guid (tpFmuPath) 
	etherGuid = get_guid (etherFmuPath) 
	gcGuid = get_guid (gcFmuPath) 
	uavCtrl1Guid = get_guid (uavctrl1FmuPath) 
	uavCtrl2Guid = get_guid (uavctrl2FmuPath) 
	uav1Guid = get_guid (uav1FmuPath) 
	uav2Guid = get_guid (uav2FmuPath) 

	jsonTemplate = os.path.join(context,"sut","SUT_template.json")
	jsonOut = os.path.join(context,"sut","SUT.json")

	with open(jsonTemplate, "rt") as fin:
		with open(jsonOut, "wt") as fout:
			for line in fin:
				#print "#-0 {0}".format(line)
				l = line.replace('@GUID_TP@', tpGuid)
				l = l.replace('@GUID_ETHER@', etherGuid)
				l = l.replace('@GUID_GC@', gcGuid)
				l = l.replace('@GUID_UC1@', uavCtrl1Guid)
				l = l.replace('@GUID_UC2@', uavCtrl2Guid)
				l = l.replace('@GUID_U1@', uav1Guid)
				l = l.replace('@GUID_U2@', uav2Guid)
				fout.write(l)

	print("## -- Successfully Updated --------------------------------------------------")

except:
	print "!! "
	print "!! Updating of GUIDs failed"
	print "!! "

