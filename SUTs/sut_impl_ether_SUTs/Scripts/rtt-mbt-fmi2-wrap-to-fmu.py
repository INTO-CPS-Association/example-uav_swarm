#! /usr/bin/env python
###############################################################
#
# Verified Systems International GmbH
#
# http://www.verified.de/
#
# Tel.  : +49 421 57204 0
# Fax   : +49 421 57204 22
# e-mail: info@verified.de
#
# -------------------------------------------------------------
#
# (C) Copyright Verified Systems International GmbH
#     $Date: $
#
# -------------------------------------------------------------
#
# Product: RTT-MBT
#
# -------------------------------------------------------------
#
# File Identification:
#
# $RCSfile:$
#
# $Header:$
#
# $Revision:$
#
# First edition by: Markus Dahlweid
# Last update by    $Author:$
#
# -------------------------------------------------------------
#
# Description:
#
# This module implements the creation of a new RTT-MBT test procedure.
# -------------------------------------------------------------

"""
"""

__version__ = "$Revision$"
# $Source$

import sys
import os
import uuid
import tempfile

from optparse import OptionParser
from lxml import etree

# Import the RTT-MBT library
import rttester
from rttester import ExitCodes, ErrorMessage

from rttester import utilities

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

from collections import namedtuple



Var = namedtuple("Var", "name type description")


template_conf = """
TILEVEL; SWI
TLA; RTT_TestProcedures
STOPONFAIL ; No
CFLAGS  ; -g
	    ; -Wall
	    ; -I../inc
	    ; -I../../inc
//INCLUDE ; rttExternDecl.h
INCLUDE ; rttModelVarDecl.h
INCLUDE ; rttInterface.h
//        ; rttSignalChecker.h

AM; am_timetick
   ;AMPROCESS	    ; am_timetick
   ;SPEC            ; fmi2sut
   ;SEED            ; 23
   ;SCRATCHPAD SIZE ; 40 k
   ;ACTIVATE        ; YES
   ;OUTPUTSTDOUT    ; YES
   ;OUTPUTFILE      ; YES

AM; sut
   ;AMPROCESS	    ; sut
   ;SPEC            ; fmi2sut
   ;SEED            ; 23
   ;SCRATCHPAD SIZE ; 40 k
   ;ACTIVATE        ; YES
   ;OUTPUTSTDOUT    ; YES
   ;OUTPUTFILE      ; YES

ADDITIONAL_RTS; fmi2adapter.rts
ADDITIONAL_RTS; ../fmi/fmi2rttInterface.rts

// Necessary compile flags to use the am_timetick hooks
// for the FMI driver component.
CFLAGS ; -I../fmi
       ; "-DAM_TIMETICK_PREFIX=fmi_timetick"
{0}


// Use the provided timing fuction from fmi2adapter.rts
// This requires RT-Tester 6.0-6.1.2 or above.
TIMERS; millisecond; fmi2_gettimeofday

// Added by RT-Tester MBT for FMI2.0 (v1.0.0)
CFLAGS ; -DDISABLE_STIMULATION

// TODO: integrate SUT

"""


template_rtt_interface = Template("""
#ifndef _XXX_RTTINTERFACE_H_XXX_
#define _XXX_RTTINTERFACE_H_XXX_
typedef struct {

{%- for var in VARS %}
{%- if var.description != "GLOBAL" %}
{{ var.type }} {{ var.name }};
{%- endif %}
{%- endfor %}

} rttInterface_t;

extern rttInterface_t* rttIOPre;
extern rttInterface_t* rttIOPost;

// ----------------------------------------------------

extern unsigned long long _timeTick;
extern unsigned long long _timeResolution;
extern int _timeTickDiff;
extern int rttHaveDiscreteTrans;

#endif
""")

template_rtt_modelvars = Template("""
#ifndef _XXX_RTTMODELVARS_H_XXX_
#define _XXX_RTTMODELVARS_H_XXX_

typedef struct {

{%- for var in VARS %}
{%- if var.description == "GLOBAL" %}
{{ var.type }} {{ var.name }};
{%- endif %}
{%- endfor %}

} rttModelVars_t;

extern rttModelVars_t* rttStatePre;
extern rttModelVars_t* rttStatePost;

#endif
""")


## ###################################################################
## AUX FUNCTIONS
## ###################################################################

def print_vars(md, var_description):
    vars = md.find("ModelVariables")
    for e in vars:
        if e.attrib['description'] == var_description:
            try:
                annot = e.find("Annotations")
                tool = annot.find("Tool")
                code = tool.find("CodeGen")
                type = code.attrib['CType']
            except:
                type = "?"
            print "{0} : {1}".format(e.attrib['name'], type)
    
def get_interface_vars(md):
    result = []
    vars = md.find("ModelVariables")
    for e in vars:
        name = (e.attrib['name']).replace("IMR.SystemUnderTest.", "IMR.sut_")
        name = name.replace("IMR.TestEnvironment.", "IMR.te__")
        name = name.replace(".", "_")
		# By rye on 20/06/2017
		# If starting with 'IMR.', then remove it. Otherwise, no change
        #name = name[4:] # remove the IMR.
        name = name.replace("IMR_", "") # 

        try:
            annot = e.find("Annotations")
            tool = annot.find("Tool")
            code = tool.find("CodeGen")
            type = code.attrib['CType']
        except:
            type = "?"
        result.append(Var(type=type, description=e.attrib['description'], name=name))
    return result

def print_input_vars(md):
    print "-- INPUT VARS: --------"
    print_vars(md, "TE2SUT")

def print_output_vars(md):
    print "-- OUTPUT VARS: -------"
    print_vars(md, "SUT2TE")


def vars_2_string(VARS, var_description, prefix, postfix):
    result = ""
    for var in VARS:
        if var.description == var_description:
            result += " {2}{0}{3} ; // {1}\n".format(var.name, var.type, prefix, postfix)
    return result


## -------------------------------------------------------------

def adjust_model_description(md, name):
    """Change the model name in an etree to name
    Also assign a (new) uuid
    """
    md.attrib['modelName'] = name
    md.attrib['guid'] = "{" + str(uuid.uuid1()) + "}"
    cosim = md.find("CoSimulation")
    cosim.attrib['modelIdentifier'] = name
    

## ###################################################################
## MAIN
## ###################################################################

# Command line parsing of the provided arguments
usage = """usage: %prog [test-procedure] [options]

Arguments:
  test-procedure      the path from the testcontext directory to the testprocedure directory

The script assumes the RTT_TESTCONTEXT ist set properly.
"""
parser = OptionParser(usage=usage, version=rttester.fmi2.get_version())
parser.add_option("--force", action="store_true", default=False, dest="force",
                  help="Force creation of FMI library and interface modules, even if they exist.")
parser.add_option("-m","--model-description", metavar="FILE", dest="interface", default=None, help="Interface (modelDescription.xml) to use for the FMU")
parser.add_option("-c","--count-sut", metavar="NUMBER", dest="sut_count", default=None, help="Append a NUMBER (as suffix) to the FMU identification")
parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose", help="Generate more output to a file 'generation.log'")

# Check that this script has received all necessary command line options
if getattr(sys, 'frozen', False):
    # The application is frozen
    filename = sys.executable
else:
    filename = __file__

basename = os.path.basename(filename)
testprocedure_path = None

(options, args) = parser.parse_args()

#print args

if len(args) == 1:
    testprocedure_path = args[0]
elif len(args) >= 2:
    ErrorMessage.report(ExitCodes.INVALID_ARGUMENTS, basename, "invalid number of arguments provided.")
else:
    testprocedure_path = "data/part"

kwargs = {"force": options.force, "is_sut": True, "sut_count": options.sut_count, "testproc_path": testprocedure_path }
if options.verbose:
    kwargs["verbose"] = True

kwargs['fmilib_path'] = os.path.join(testprocedure_path, "fmi")

#os.environ['RTT_TESTCONTEXT'] = os.getcwd()
os.chdir(os.environ['RTT_TESTCONTEXT'])

if options.interface:
    print "## Using modelDescription.xml = '{0}'".format(options.interface)
    print(rttester.fmi2.get_tool_description())
	# By rye on 20/06/2017
	# This should be true to use user supplied model description
    kwargs['fmi_model_description_customised'] = True
    fmi = rttester.fmi2(**kwargs)
    print "## [0] modelDescription = '{0}'".format(fmi.fmi_model_description_path)
    fmi.fmi_model_description_path = options.interface
    print "## [1] modelDescription = '{0}'".format(fmi.fmi_model_description_path)
    print "fmi.fmilib_root = {0}".format(fmi.fmilib_root)
    print "fmi.get_fmi_model_name() = {0}".format(fmi.get_fmi_model_name())
    specsdir = os.path.join(fmi.testcontext, testprocedure_path, "specs")
    incdir   = os.path.join(fmi.testcontext, testprocedure_path, "inc")
    confdir = os.path.join(fmi.testcontext, testprocedure_path, "conf")
    utilities.mkdir_p(specsdir)
    utilities.mkdir_p(incdir)
    utilities.mkdir_p(confdir)
    print "## [2] modelDescription = '{0}'".format(fmi.fmi_model_description_path)
    fmi.generate_model_description()
    print "## OK: Did parse model description"
    adjust_model_description(fmi.fmi_model_description, fmi.get_fmi_model_name())
    #fmi.fmi_model_description_path = fmi.fmi_model_description_path + "_NEW"
    fd, modified_model_description_path = tempfile.mkstemp()
    os.close(fd)
    utilities.rm_f(modified_model_description_path)
    print "TMPFILE: {0}".format(modified_model_description_path)
    print "## [3] modelDescription = '{0}'".format(fmi.fmi_model_description_path)
    fmi.fmi_model_description_path = modified_model_description_path
    print "## [4] modelDescription = '{0}'".format(fmi.fmi_model_description_path)
    fmi.generate_model_description()
    #with open(modified_model_description_path, "r") as input_file:
    #    for line in input_file:
    #        sys.stdout.write(line)
    #raise("X")
    #print etree.tostring(fmi.fmi_model_description, encoding='UTF-8', xml_declaration=True, pretty_print=True) 
    #raise("DEBUG")
    print_input_vars(fmi.fmi_model_description)
    print_output_vars(fmi.fmi_model_description)
    print "## Creating interface library in '{0}' [fmilib_path={1}]".format(fmi.fmilib_root, fmi.fmilib_path)
    utilities.mkdir_p(os.path.join(fmi.testcontext, fmi.fmilib_root))
    #raise("X-1")
    fmi.generate_interface_library()
    #raise("X-3")
    utilities.cp_f(os.path.join(fmi.template_path, "fmi2adapter.rts"), specsdir)
    # write AM for sut operations and add note on mapping input / output
    interface_vars = get_interface_vars(fmi.fmi_model_description)
    print "interface_vars={0}".format(interface_vars)
    input_var_desc = "Map FMU input variables to SUT: X = rttIOPre->X\n\n" + vars_2_string(interface_vars, "TE2SUT", "? = rttIOPre->","")
    output_var_desc = "Map SUT output variables to FMU output: rttIOPost->X = X\n\n" + vars_2_string(interface_vars, "SUT2TE", "rttIOPost->? = ","")

    with open(os.path.join(fmi.template_path, "fmi2sut.rts"), "r") as input_file:
        with open(os.path.join(specsdir, "fmi2sut.rts"), "w") as output_file:
            output_file.writelines(utilities.sed_g("\@FMU_OUTPUT_VARS\@", output_var_desc, utilities.sed_g("\@FMU_INPUT_VARS\@", input_var_desc, input_file)))
    conffile = os.path.join(confdir, "swi.conf")
    if sys.platform.startswith('win'):
        os_ld=""
    else:
        os_ld="LDFLAGS ; -lrt"
    with open(conffile, "w") as output_file:
        output_file.write(template_conf.format(os_ld))
    interface_file = os.path.join(incdir, "rttInterface.h")    
    
    with open(interface_file, "w") as output_file:
        output_file.write(template_rtt_interface.render(VARS=interface_vars))
    modelvars_file = os.path.join(incdir, "rttModelVarDecl.h")    
    with open(modelvars_file, "w") as output_file:
        output_file.write(template_rtt_modelvars.render(VARS=interface_vars))

    print "## Call: build_fmu()"    
    fmi.build_fmu(testprocedure_path)    
    utilities.rm_f(modified_model_description_path)
