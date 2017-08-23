#! /usr/bin/env python
# This script tries to guess-configure a set of FMUs
# and starts a simulation using a running COE.
#
# Initial Version by: Florian Lapschies, Verified Systems International GmbH


import os
import glob
import sys
import zipfile
import xml.etree.ElementTree as ET
import json
import tempfile
import httplib
from optparse import OptionParser

usage = """usage: run-COE.py  TestProc1 TestProc2 [TestProc3, ... ]

Starts an test execution with two FMUs that are (from RT-Tester perspective)
RTT6 test procedures wrapped in FMUs.

	TestProc1		: The test driver (directing stimulation and checking)
	TestProc2,3,...  : The system under test (SUT)
					   which is compared to the expected behaviour

The COE will check whether all inputs/outputs fit together; it is a user obligation
to contruct the TestProcs such that the corresponding FMU interfaces
constitute a closed system.
"""

__version__ = "$Revision: 11063 $".replace("$", "").replace("Revision:", "").replace(" ", "")

global RUN_DURATION
global STEP_SIZE

global verbose
verbose = True

## ###################################################################
## AUX FUNCTIONS
## ###################################################################


def blurt(str):
	if(verbose):
		sys.stderr.write(str + "\n")

def py(scriptcall):
	"""Invoking another python script (possibly with interpreter)"""
	blurt("Invoking [" + sys.platform + "] " + scriptcall)
	if sys.platform.startswith('win'):
		ret = os.system("C:\\Python27\\python.exe" + " " + scriptcall)
	else:
		ret = os.system(scriptcall)
	return (0 == ret)

class Variable:
	def __init__(self, name):
		self.name = name
		self.sourceFMU = None
		self.sinkFMUs = set()
	def __eq__(self, other):
		return isinstance(other, Variable) and self.name == other.name
	def __neq__(self, other):
		return not self.__eq__(other)
	def __cmp__(self, other):
		return self.name.__cmp__(other)
	def __hash__(self):
		return self.name.__hash__()
	def __str__(self):
		return self.name
	def setSourceFMU(self, source):
		# rye: 
		#if self.sourceFMU != None:
		#	raise Exception("Variable " + self.name + " is output of FMU " + str(self.sourceFMU)
		#					+ " as well as " + str(source) + ".")
		#else:
		#	self.sourceFMU = source
		self.sourceFMU = source
	def getName(self):
		return self.name
	def addSinkFMU(self, sink):
		self.sinkFMUs.add(sink)
	def getSourceFMU(self):
		return self.sourceFMU
	def getSinkFMUs(self):
		return self.sinkFMUs

class Variables:
	variables = {}
	@classmethod
	def getByName(cls, name):
		if name in cls.variables:
			return cls.variables.get(name)
		else:
			v = Variable(name)
			cls.variables[name] = v
			return v
	@classmethod
	def getAll(cls):
		return cls.variables.values()

class FMU:
	instanceCounter = 0

	def __init__(self, fileName):
		self.fileName = os.path.abspath(fileName)
		self.guid = ""
		self.inputs = set()
		self.outputs = set()
		self.instanceName = "fmu" + str(FMU.instanceCounter)
		self.stopTime = "20.0"
		self.stepSize = "0.001"
		FMU.instanceCounter = FMU.instanceCounter + 1

		print "Instance name: {0} <--> {1}".format(self.instanceName, fileName)
		with zipfile.ZipFile(self.fileName, 'r') as zip:
			print "Scanning file " + self.fileName

			modelDescritionXML = zip.read("modelDescription.xml")
			rootNode = ET.fromstring(modelDescritionXML)			
			self.guid = rootNode.get("guid")
			for node in rootNode.findall("./ModelVariables/ScalarVariable[@causality='input']"):
				variable = Variables.getByName(node.get("name"))
				variable.addSinkFMU(self)
				self.inputs.add(variable);
			for node in rootNode.findall("./ModelVariables/ScalarVariable[@causality='output']"):
				variable = Variables.getByName(node.get("name"))
				variable.setSourceFMU(self)
				self.outputs.add(variable);

			print "guid = " + self.guid
			for v in self.inputs: print "input " + str(v)
			for v in self.outputs: print "output " + str(v)
			try:
				de = rootNode.findall("DefaultExperiment")
				#print de
				self.stopTime = de[0].get("stopTime")
				self.stepSize = de[0].get("stepSize")
			except:
				print "{0}: Unable to extract stopTime/stepSize from DefaultExperiment, falling back to defaults ({1}, {2})".format(self.instanceName, self.stopTime, self.stepSize)
				pass

	def getFileName(self):
		return self.fileName
	def getGUID(self):
		return self.guid
	def getGUIDInstanceName(self):
		return self.guid + "." + self.instanceName
	def setAvailableLogLevels(self, levels):
		self.availableLogLevels = levels
	def getAvailableLogLevels(self):
		return self.availableLogLevels

	def __str__(self):
		return self.fileName


def prettyPrintJSONPayload(rawData):
	try:
		j = json.loads(rawData)
		return json.dumps(j, indent=4)
	except:
		return rawData


class COE:
	fmus = []
	version = None

	def __init__(self, fileNames, port=None, ioconfig=None, connections_file=None):
		 if port:
			 self.host = "localhost:{0}".format(port)
		 else:
			 self.host = "localhost:8082"
		 self.ioconfig = ioconfig
		 self.connections_file = connections_file
		 self.fmus = []
		 for fileName in fileNames:
			self.fmus.append(FMU(fileName))
		 self.version_is_SNAPSHOT = True

		 if self.fmus and (RUN_DURATION == "auto"):
			 print "Run duration 'auto': taking it from 'stopTime' of first FMU (+ 1.0 second)"
			 self.run_duration = 1.0 + float(self.fmus[0].stopTime)
		 else:
			 self.run_duration = float(RUN_DURATION)

		 if self.fmus and (STEP_SIZE == "auto"):
			 print "Step Size 'auto': taking stepSize first FMU"
			 self.stepsize	   = float(self.fmus[0].stepSize)
		 else:
			 self.stepsize	   = float(STEP_SIZE)
		 if self.fmus:
			 print "## NOTE: using run duration {0:4.4f} [s] / step size {1:4.4f} [s]".format(self.run_duration, self.stepsize)

		 try:
			 version_string = self.query_version()
			 self.version = version_string.replace("-SNAPSHOT", "")
			 self.version_list = map(int, self.version.split('.'))
			 if -1 == version_string.find("-SNAPSHOT"):
				 self.version_is_SNAPSHOT = False
		 except:
			 self.version = "unknown"
			 self.version_list = [ 0, 0, 0 ]

	def version_atleast(self, version_to_compare_to):
		"""Check whether the coe has at least a specific version number.
		The version_to_compare_to must be given as string 'x.y.z'
		If the coe version cannot be determined, the result is always False
		"""
		try:
			cmp_v  = map(int, version_to_compare_to.split('.'))
			if self.version_list[0] < cmp_v[0]:
				return False
			elif self.version_list[0] > cmp_v[0]:
				return True
			if self.version_list[1] < cmp_v[1]:
				return False
			elif self.version_list[1] > cmp_v[1]:
				return True
			return (self.version_list[2] >= cmp_v[2])
		except:
			return False


	def getConfigurationJSON(self):
		if self.ioconfig and "connections" in self.ioconfig.keys():
			return self.ioconfig

		fmus = {}
		for f in self.fmus:
			if self.version_atleast("0.1.0"):
				fmus[f.guid] = ("file:" + f.getFileName().replace("C:","")).replace("\\", "/")
			else:
				fmus[f.guid] = f.getFileName()
		connections = {}
		all_inputs = {}
		for v in Variables.getAll():
			source = v.getSourceFMU()
			if source is None:
				print "NOTE: skipping variable {0} (no source identified)".format(v)
			else:
				print "source[var={1}] = {0}".format(source, v)
				input = source.getGUIDInstanceName() + "." + v.getName()
				outputs = [f.getGUIDInstanceName() + "." + v.getName() for f in v.getSinkFMUs()]
				connections[input] = outputs
				try:
					if all_inputs[source.getGUIDInstanceName()]:
						(all_inputs[source.getGUIDInstanceName()]).append(v.getName())
				except:
					all_inputs[source.getGUIDInstanceName()] = [v.getName()]
		parameters = {}
		algorithm = {
			"type" : "fixed-step",
			"size" : self.stepsize
		}
		config = {
			"fmus" : fmus,
			"connections" : connections,
			"parameters" : parameters,
			"algorithm" : algorithm
		}
		## add more parameters if version is higher
		if self.version_atleast("0.1.0"):
			config["livestream"] = { }
			config["logVariables"] = all_inputs

		# overwrite
		if self.connections_file:
			fd, modified_connection = tempfile.mkstemp()
			os.close(fd)
			guids = {}
			idx = 1
			for f in self.fmus:
				guids[idx] = f.guid
				idx = idx + 1

			with open(self.connections_file, "r") as in_file:
				with open(modified_connection, "w") as out_file:
					for line in in_file:
						out_line = line
						idx = 1
						while idx <= len(self.fmus):
							out_line = out_line.replace("@GUID_TP{0}@".format(idx), guids[idx])
							idx = idx + 1
						out_file.write(out_line)

			with open(modified_connection) as json_data:
				connections = json.load(json_data)
				print "## Using connections information from file '{0}'".format(self.connections_file)
				if verbose:
					prettyPrintJSONPayload(connections)
			if "connections" in connections.keys():
				print "## Note: using connections[] setting from --connections FILE"
				config["connections"] = connections["connections"]
			else:
				print "## Note: using --connections FILE as connections[]"
				config["connections"] = connections
			os.remove(modified_connection)


		return config

	def getFMUByGUIDInstanceName(self, name):
		for f in self.fmus:
			if f.getGUIDInstanceName() == name:
				return f
		return None

	def sendCommand(self, command, payload = None, contentType = "application/json", requestIsJson = True, responseIsJson = True):
		conn = httplib.HTTPConnection(self.host)
		headers = {}
		blurt("## ContentType: " + contentType)
		if contentType != None:
			headers = {"Content-Type": "application/json"}
		if payload and requestIsJson:
			payload = json.dumps(payload, indent=4)
			blurt("## Sending command \"" + command + "\" with payload\n" + payload)
		else:
			blurt("## Sending command \"" + command + "\"")
		conn.request("POST", command, payload, headers)
		res = conn.getresponse()
		data = res.read()
		conn.close()
		if responseIsJson:
			blurt("## Received response:\n" + prettyPrintJSONPayload(data))
			return json.loads(data)
		else:
			return data

	def status(self, id = None):
		url = "/status/"
		if id != None:
			url += str(id)
		return self.sendCommand(url)

	def createSession(self):
		url = "/createSession"
		response = self.sendCommand(url)
		self.sessionId = response["sessionId"]
		return self.sessionId		 

	def initialize(self):
		url = "/initialize/" + str(self.sessionId)
		response = self.sendCommand(url, payload = self.getConfigurationJSON())
		print "response: {0}".format(response)
		response = response[0]
		avaliableLogLevels = response["avaliableLogLevels"]
		for instanceName in avaliableLogLevels:
			print "initialize instance: {0}".format(instanceName)
			fmu = self.getFMUByGUIDInstanceName(instanceName)
			print "instances in availableLogLevels: {0} and fmu: {1}".format(instanceName, fmu)
			fmu.setAvailableLogLevels(avaliableLogLevels[instanceName])
		return response

	def query_version(self):
		url = "/version" 
		response = self.sendCommand(url)
		return response["version"]

	def simulate(self):
		url = "/simulate/" + str(self.sessionId)
		logLevels = {}
		for fmu in self.fmus:
			logLevels[fmu.getGUIDInstanceName()] = [lvl["name"] for lvl in fmu.getAvailableLogLevels()]
		payload = {}
		payload["startTime"] = 0.0
		payload["endTime"] = self.run_duration
		payload["logLevels"] = logLevels
		return self.sendCommand(url, payload = payload)

	def result(self, outFile):
		url = "/result/" + str(self.sessionId)
		if os.path.splitext(outFile)[1] == ".zip":
			contentType = "application/zip"
			url += "/zip"
		else:
			contentType = "text/plain"
		data = self.sendCommand(url, contentType = contentType, responseIsJson = False)
		blurt("## Writing file " + os.path.realpath(outFile))
		with open(outFile, 'wb') as f:
			f.write(data)

	def getFirstTestProc(self):
		if self.fmus:
			fmu0 = self.fmus[0]
			file = fmu0.getFileName()
			dir  = os.path.dirname(file)
			if(os.path.isabs(dir)):
				return dir.replace("\\", "/").replace((os.environ['RTT_TESTCONTEXT'] + "/").replace("\\", "/"), "")
			else:
				return dir.replace("\\", "/")
		else:
			return None

	def getSecondTestProc(self):
		if self.fmus:
			fmu1 = self.fmus[1]
			file = fmu1.getFileName()
			dir  = os.path.dirname(file)
			if(os.path.isabs(dir)):
				return dir.replace("\\", "/").replace((os.environ['RTT_TESTCONTEXT'] + "/").replace("\\", "/"), "")
			else:
				return dir.replace("\\", "/")
		else:
			return None

	def destroy(self):
		url = "/destroy/" + str(self.sessionId)
		return self.sendCommand(url, responseIsJson=False)

## -- MAIN -----------------------------------------------------------------

parser = OptionParser(usage=usage, version=__version__)
parser.add_option("-t","--timeout", metavar="DURATION", dest="duration", default="10.0", help="define the duration of the run (in seconds).\nIf this value is set to 'auto', then the duration is taken from the DefaultExperiment of the first FMU (+ 1.0 second slack added).")
parser.add_option("-s","--stepsize", metavar="DURATION", dest="stepsize", default="0.1", help="define the step size the COE shall use (in seconds), default: 0.1.\nIf this value is set to 'auto', then the step size is taken from the DefaultExperiment of the first FMU.")
parser.add_option("-p","--port", metavar="PORT", dest="port", default=None, help="define the port to connect with the COE")
parser.add_option("-c","--query-coe-version", action="store_true", dest="version", default=False, help="Query the version of the COE, display it and exit")
parser.add_option("-i","--io-config", metavar="FILE", dest="ioconfig", default=None, help='Point to an override *.json file that defines the COE configuration; needs to map "connections", ')
parser.add_option("-C","--connections", metavar="FILE", dest="connections_file", default=None, help='Point to an override *.json file that defines connections as connections["<input>"] =  [ <output>* ]\nThe <input>/<output> is strucutured as fmuName.instanceName.varName\nThe data from this file will be used in the COE run *instead* of the derived connections[].\nThe place holders @GUID_TP1@, @GUID_TP2@, ... can be used to reference the respective GUID of the respective TestProc.')
parser.add_option("-q","--quiet", action="store_true", dest="quiet", default=False, help="Suppress debugging output")
parser.add_option("--verbose", action="store_true", dest="verbose", default=False, help="Print all debugging output")

(options, args) = parser.parse_args()


RUN_DURATION = options.duration
STEP_SIZE	= options.stepsize

if options.verbose:
	verbose = True
elif options.quiet:
	verbose = False

if options.version:
	print "Own version: " + __version__
	coe = COE([], port=options.port)
	print "COE version: " + coe.version
	sys.exit(0)


ioconfig = None
if options.ioconfig:
	if os.path.exists(options.ioconfig):
		with open(options.ioconfig) as json_data:
			ioconfig = json.load(json_data)
			print "## Using io-config information from file '{0}'".format(options.ioconfig)
			if verbose:
				prettyPrintJSONPayload(ioconfig)
			if options.connections_file:
				print "WARNING: since option --io-config is given, the --connections part will be ignored!"
				options.connections_file = None
	else:
		print "## NOTE: paramter to --io-config '{0}' did not point to a readable file, ignoring!"

connections_file = None
if options.connections_file:
	if os.path.exists(options.connections_file):
		connections_file = options.connections_file
	else:
		print "## NOTE: paramter to --connections '{0}' did not point to a readable file, ignoring!"


if len(args) == 0:
	print usage
	sys.exit(0)
else:
	fmuFiles = []
	for f in args:
		if os.path.isfile(f):
			fmuFiles = fmuFiles + [f]
		elif os.path.isdir(f):
			candidates = glob.glob(os.path.join(f, "*.fmu"))
			if len(candidates) == 0:
				sys.stderr.write("ERROR: cannot find an *.fmu in directory '{0}'\n".format(f))
				sys.exit(1)
			elif len(candidates) == 1:
				fmuFiles = fmuFiles + [candidates[0]]
			else:
				first = candidates[0]
				sys.stderr.write("WARNING: found several *.fmu in directory '{0}', selecting first: {1}\n".format(f, first))
				fmuFiles = fmuFiles + [first]
		else:
			sys.stderr.write("ERROR: argument '{0}' does not denote a FMU\n".format(f))
			sys.exit(1)

print "Starting COE with:"
print fmuFiles

print "OSLC-Recording Start"
try:
	util_dir = os.path.join(os.environ['RTT_TESTCONTEXT'], "..", "utils")
	py('"{0}"'.format(os.path.join(util_dir, 'rtt-fmi-report-queue.py')))
except:
	pass


coe = COE(fmuFiles, port=options.port, ioconfig=ioconfig, connections_file=connections_file)
print "## NOTE: COE version is {0} ({1})".format(coe.version, coe.version_list)
if coe.version_is_SNAPSHOT:
	print "WARNING: This version of the coe is marked as SNAPSHOT (or unknown), might be incomplete!"
coe.createSession()
coe.initialize()
coe.simulate()
# coe.result("out.zip")
coe.result("out.csv")
coe.destroy()
coe.status()

print "Computing Trace Results (Testcases/Requirements)"
try:
	prog = os.path.join(os.environ['RTTDIR'], 'bin', 'rtt-trace-results.py')
	tp   = coe.getFirstTestProc()
	py('"{0}" --req-trace {1}'.format(prog, tp))
except:
	print "WARNING: Failure in computing tracing information"

#try:
#	prog = os.path.join(os.environ['RTTDIR'], 'bin', 'rtt-trace-results.py')
#	tp   = coe.getSecondTestProc()
#	py('"{0}" --req-trace {1}'.format(prog, tp))
#except:
#	print "[1] WARNING: Failure in computing tracing information"

print "Collecting Signals"
try:
	prog = os.path.join(os.environ['RTTDIR'], 'bin', 'rtt-collect-signals.py')
	tp   = coe.getFirstTestProc()
	py('"{0}" -o {1}/testdata/signals.dat {1}/testdata'.format(prog, tp))
except:
	print "WARNING: Failure in computing signal information"

try:
	prog = os.path.join(os.environ['RTTDIR'], 'bin', 'rtt-collect-signals.py')
	tp   = coe.getSecondTestProc()
	py('"{0}" -o {1}/testdata/signals.dat {1}/testdata'.format(prog, tp))
except:
	print "[1] WARNING: Failure in computing signal information"

print "OSLC Submitting"
try:
	util_dir = os.path.join(os.environ['RTT_TESTCONTEXT'], "..", "utils")
	tp_id = os.path.basename(os.path.dirname(fmuFiles[0]))
	py(' '.join(['"{0}"'.format(os.path.join(util_dir, 'rtt-fmi-queue-event.py')), 'Run-Test', '"' + os.environ['RTT_TESTCONTEXT'] + '"', tp_id ]))

	py('"{0}"'.format(os.path.join(util_dir, 'rtt-fmi-report-queue.py')))
except:
	print "NOTE: Failure in OSLC resporting (missing environment setting for OSLC_SERVER ?)"

