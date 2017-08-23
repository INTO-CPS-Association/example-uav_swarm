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
# This module globally defines the exit codes for RTT-MBT.
# It also implements a class, which should be used to generate
# consistent error messages to the user.
#
# -------------------------------------------------------------

"""
This module globally defines the exit codes for RTT-MBT.
It also implements a class, which should be used to generate
consistent error messages to the user.
"""

import sys
import os
import uuid
import datetime
import utilities
import tempfile
import zipfile
import glob
import shutil
import socket

from lxml import etree

# Import the RTT-MBT library
from errors import *
from projectdb import *
from mbt import *
from projectdb import *

__version__ = "$Revision$"
# $Source$


class fmi2:
    def __init__(self, force=False, fmimodel_path=None, fmilib_path=None, generation_context=None,
                 is_simulation=False, is_sut=False, sut_count=None, testproc_path=None, fmi_model_description_customised=False, verbose=False, *args):
        if ('RTT_TESTCONTEXT' not in os.environ) or (not os.path.exists(os.environ['RTT_TESTCONTEXT'])):
            ErrorMessage.throw(ExitCodes.RTT_TESTCONTEXT_UNDEFINED)

        self.verbose = verbose
        self.is_simulation = is_simulation
        self.is_sut = is_sut
        self.testproc_path = testproc_path
        self.sut_count = sut_count
        self.force = force
        self.testcontext = os.environ['RTT_TESTCONTEXT']
        if os.environ.get("RTT_PROJECT"):
            self.rtt_project = os.environ["RTT_PROJECT"]
        else:
            self.rtt_project = os.path.join(self.testcontext, "project.rtp")

        self.toolrootdir= MBT.installPath
        self.template_path = os.path.join(self.toolrootdir, "templates/fmi")
        self.toolbindir = os.path.join(self.toolrootdir, "bin")

        self.projectdb_path = os.path.join(self.testcontext, "model", "model_dump.db")
        self.projectdb = MBTProjectDB(self.projectdb_path, self.template_path)

        self.fmi_model_description = None
        if fmimodel_path is None:
            self.fmi_model_description_path = os.path.join(self.testcontext, "model", "modelDescription.xml")
        else:
            self.fmi_model_description_path = os.path.join(fmimodel_path, "modelDescription.xml")
        self.fmi_model_description_customised = fmi_model_description_customised

        if generation_context is None:
            self.generation_context = self.testcontext
        else:
            self.generation_context = generation_context

        if fmilib_path is None:
            self.fmilib_rel_path = "fmi"
            self.fmilib_root = os.path.join(self.testcontext, "fmi")
        else:
            if os.path.isabs(fmilib_path):
                self.fmilib_rel_path = (fmilib_path.replace("\\", "/")).replace(self.testcontext.replace("\\", "/") + "/", "")
                self.fmilib_root = fmilib_path
            else:
                self.fmilib_rel_path = fmilib_path.replace("\\", "/")
                self.fmilib_root = os.path.join(self.testcontext, fmilib_path)

        self.fmilib_path = os.path.join(self.fmilib_root, self.get_fmi_model_name() + self.__get_sharedlib_extension())
        pass

    @staticmethod
    def get_version():
        return "1.0.0"

    @staticmethod
    def get_tool_description():
        """
        Returns the current version of the tool.
        :return: string Version number
        """
        return "RT-Tester MBT for FMI2.0 (v" + fmi2.get_version() + ")"

    def get_fmi_model_name(self):
        model_name = self.projectdb.get_model_name()
        if self.is_sut:
            model_name += "_sut"
            if self.sut_count:
                model_name += self.sut_count
        elif self.is_simulation:
            #!o!model_name += "_simulation"
            pos = self.generation_context.rfind(os.path.sep)
            model_name += "_" + (self.generation_context[pos+1:]).lower()
        return model_name

    def generate_model_description(self):
        """
        This method either creates a new FMI XML description file or loads the existing one.
        :return: None
        """
        if not os.path.exists(self.fmi_model_description_path) or self.force:
            (path, fname) = os.path.split(self.fmi_model_description_path)
            if not os.path.exists(path):
                utilities.mkdir_p(path)

            print("Creating output file '{0}'.".format(self.fmi_model_description_path))
            self.fmi_model_description = self.__build_fmi_model_description()
            with open(self.fmi_model_description_path, "w") as xmloutput:
                xmloutput.write(etree.tostring(self.fmi_model_description,
                                               encoding='UTF-8', xml_declaration=True, pretty_print=True))
        else:
			print "## [fmi2] modelDescription = '{0}'".format(self.fmi_model_description_path)
			fmi_model_descriptionTree = etree.parse(self.fmi_model_description_path)
			self.fmi_model_description = fmi_model_descriptionTree.getroot()
			print "## [fmi2] generated modelDescription = '{0}'".format(self.fmi_model_description)
        pass

    def __build_fmi_model_description(self):
        """
        Generates an XML document describing the external interfaces of the
        model currently stored inthe project data base. This XML document
        conforms to the rules defined in the FMI 2.0 standard for Co-Simulation.
        :return: XML document root node
        """
        fmi_model_description = etree.Element("fmiModelDescription",
                                              fmiVersion="2.0",
                                              modelName=self.get_fmi_model_name(),
                                              guid="{" + str(uuid.uuid1()) + "}",
                                              generationTool=fmi2.get_tool_description(),
                                              generationDateAndTime=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z"),
                                              version=str(self.projectdb.get_model_id()),
                                              variableNamingConvention="structured")

        fmi_model_description.append(etree.Element("CoSimulation",
                                                   modelIdentifier=self.get_fmi_model_name(),
                                                   canHandleVariableCommunicationStepSize="true",
                                                   canBeInstantiatedOnlyOncePerProcess="true"))

        logCategories = etree.Element("LogCategories")
        fmi_model_description.append(logCategories)
        logCategories.extend([
            etree.Element("Category", name="logRtTester",
                          description="Log all events which are send from the RT-Tester test processes."),
            etree.Element("Category", name="logEvents",
                          description="Log all events (during initialization and simulation)."),
            etree.Element("Category", name="logStatusWarning",
                          description="Log messages when returning fmi2Warning status from any function."),
            etree.Element("Category", name="logStatusDiscard",
                          description="Log messages when returning fmi2Discard status from any function."),
            etree.Element("Category", name="logStatusError",
                          description="Log messages when returning fmi2Error status from any function."),
            etree.Element("Category", name="logStatusFatal",
                          description="Log messages when returning fmi2Fatal status from any function."),
            etree.Element("Category", name="logStatusPending",
                          description="Log messages when returning fmi2Pending status from any function."),
            etree.Element("Category", name="logAll",
                          description="Log all messages.")]
        )

        if self.fmi_model_description_customised:
            print "## Note: using ModelVariables from command line input (--model-description)"
            fmi_model_description.append(self.fmi_model_description.find("ModelVariables"))
            fmi_model_description.append(self.fmi_model_description.find("ModelStructure"))
            return fmi_model_description

        modelVariables = etree.Element("ModelVariables")
        fmi_model_description.append(modelVariables)

        modelStructure = etree.Element("ModelStructure")
        fmi_model_description.append(modelStructure)
        modelOutputs = etree.Element("Outputs")
        initialUnknowns = etree.Element("InitialUnknowns")
        modelStructure.append(modelOutputs)
        modelStructure.append(initialUnknowns)

        self.__build_modelVariables(modelVariables, modelOutputs, initialUnknowns)

        return fmi_model_description

    def __create_output(self, scalar, scalar_index, modelOutputs, initialUnknowns):
        scalar.attrib['causality'] = "output"
        scalar.attrib['variability'] = "discrete"

        modelOutputs.append(etree.Element("Unknown", index=str(scalar_index), dependencies=""))
        initialUnknowns.append(etree.Element("Unknown", index=str(scalar_index)))
        pass

    def __create_input(self, scalar, initial_value, typeelem):
        scalar.attrib['causality'] = "input"
        scalar.attrib['variability'] = "discrete"
        typeelem.attrib['start'] = str(initial_value)
        pass

    def __add_default_experiment(self, fmi_model_description_path, signals_json_path):
        min_idx, max_idx, signal_data, signal_types, time_stamp_map = self.projectdb.process_signals_json(signals_json_path)
        # Expected duration in milliseconds:
        expected_duration = math.ceil(time_stamp_map[max_idx]/1000.0) + 1.0

        model_description = etree.parse(fmi_model_description_path)

        logcat = model_description.find(".//LogCategories")
        parent = logcat.getparent()
        default_experiment = etree.Element("DefaultExperiment")
        default_experiment.attrib['startTime'] = str(0.0)
        default_experiment.attrib['stopTime'] = str(expected_duration)
        default_experiment.attrib['stepSize'] = str(0.001)
        default_experiment.attrib['tolerance'] = str(0.000)

        parent.insert(parent.index(logcat) + 1, default_experiment)
        with open(fmi_model_description_path, "w") as xmloutput:
            xmloutput.write(etree.tostring(model_description, encoding='UTF-8',
                                           xml_declaration=True, pretty_print=True))

    def __build_modelVariables(self, modelVariables, modelOutputs, initialUnknowns):
        """
        This is a helper function, that populates the XML nodes of the XML document
        with information about the interface variables of the RT-Tester MBT model.
        :param modelVariables: The XML element <ModelVariables>
        :param modelOutputs: The XML element <ModelOutputs>
        :param initialUnknowns: The XML element <InitialUnknown>
        :return: None
        """
        if self.fmi_model_description_customised and False:
            attributes = self.__get_attributes_from_model_description()
            modelVariables = self.fmi_model_description.find("ModelVariables")
            return
        attributes = self.projectdb.get_model_attributes()
        scalar_index = 0
        value_references = dict()

        for attribute in attributes:
            # We are skipping all internal variables of type "clock"
            if attribute["Type"] == "clock":
                continue

            # Extract all relevant information from dictionary object
            print "## add modelVariable: {0} [InterfaceName={1}]".format(attribute['FullName'], attribute['InterfaceName'])
        
            full_name = attribute['FullName']
            stereotype = attribute['Stereotype']
            type_name = self.__map_mbt_fmi_types(attribute['Type'])
            initial_value = attribute['InitialValue']

            value_reference = 1
            if value_references.has_key(type_name):
                value_reference = value_references[type_name] + 1
            value_references[type_name] = value_reference

            scalar_index += 1
            scalar = etree.Element("ScalarVariable",
                                   name=full_name,
                                   valueReference=str(value_reference),
                                   description=stereotype)
            typeelem = etree.Element(type_name)
            scalar.append(typeelem)

            if stereotype == "SUT2TE":
                # This is an output of the SUT: therefore an output of a simulation, and an input for a test.
                if self.is_simulation or self.is_sut:
                    self.__create_output(scalar, scalar_index, modelOutputs, initialUnknowns)
                else:
                    self.__create_input(scalar, initial_value, typeelem)
            elif stereotype == "TE2SUT":
                # This is an input to the SUT: therefore an input to a simulation, and an output of a test.
                if self.is_simulation or self.is_sut:
                    self.__create_input(scalar, initial_value, typeelem)
                else:
                    self.__create_output(scalar, scalar_index, modelOutputs, initialUnknowns)
            else:
                # These are either GLOBAL or LOCAL
                scalar.attrib['causality'] = "local"
                scalar.attrib['variability'] = "discrete"
                initialUnknowns.append(etree.Element("Unknown", index=str(scalar_index)))

            if (type_name != "Boolean") and (attribute["MinValue"] != ""):
                typeelem.attrib['min'] = attribute["MinValue"]
            if (type_name != "Boolean") and (attribute["MaxValue"] != ""):
                typeelem.attrib['max'] = attribute["MaxValue"]

            # RT-Tester specific annotations
            annotations = etree.Element("Annotations")
            tool = etree.Element("Tool")
            tool.attrib["name"] = "RT-Tester"
            annotations.append(tool)

            codegen = etree.Element("CodeGen")
            codegen.attrib["CName"] = attribute["InterfaceName"]
            codegen.attrib["CType"] = attribute["InterfaceType"]
            codegen.attrib["ModelType"] = attribute["Type"]
            tool.append(codegen)
            scalar.append(annotations)

            modelVariables.append(scalar)

    @staticmethod
    def __map_mbt_fmi_types(mbttype):
        """
        Mapping helper function to construct FMI type names from RT-Tester MBT type names.
        :param mbttype: string describing the model internal type
        :return: a type name of a type defined by the FMI 2.0 standard.
        """
        if mbttype == "int":
            return "Integer"
        elif mbttype == "float":
            return "Real"
        elif mbttype == "double":
            return "Real"
        elif mbttype == "bool":
            return "Boolean"
        else:
            raise MBTError("Unknown MBT type '{0}'.".format(mbttype),1)

    def generate_interface_library(self):
        """
        Create the global FMI interface library for the RT-Tester MBT model
        stored in the project data base. Additionally the interface module
        for RT-Tester test procedures is created, that can be used to
        automatically connect RT-Tester MBT test procedures to the FMI library.
        :return: None
        """
        if self.verbose:
            print "## generate_interface_library() in generation context {0} is_SUT={1}".format(self.generation_context, self.is_sut)

        if self.is_sut and (self.fmilib_root is os.path.join(self.testcontext, "fmi")) and os.path.exists(self.fmilib_root) and False:
            print "NOTE: generate_interface_library() skipping generation context {0} is_SUT={1}".format(self.generation_context, self.is_sut)
            return

        rebuild = self.force

        if not os.path.exists(self.fmilib_path):
            # If the shared lib does not exist, create it.
            rebuild = True
        else:
            # If the shared library is older than the modelDescription.xml, re-create it.
            mtime_xml = os.path.getmtime(self.fmi_model_description_path)
            mtime_lib = os.path.getmtime(self.fmilib_path)
            if mtime_lib < mtime_xml:
                rebuild = True

        if rebuild:
            if self.verbose:
                print "DO: __create_interface_library()"
            self.__create_interface_library()
            if (not self.is_sut):
                if self.verbose:
                    print "DO: __copy_rttester_files()"
                self.__copy_rttester_files()
            if self.verbose:
                print "DO: __build_interface_library()"
            self.__build_interface_library()

    def __copy_rttester_files(self):
        """
        Create the necessary directories in the test context and copy the
        files from the template directory into those directories.
        :return: None
        """
        specsdir = os.path.join(self.generation_context, "specs")
        if not os.path.exists(specsdir):
            os.mkdir(specsdir)
        if not os.path.isdir(specsdir):
            ErrorMessage.throw(ExitCodes.FILE_NOT_FOUND, specsdir)

        if self.is_sut:
            confdir = os.path.join(self.generation_context, self.testproc_path, "conf")
        else:
            confdir = os.path.join(self.generation_context, "conf")
        if not os.path.exists(confdir):
            os.mkdir(confdir)
        if not os.path.isdir(confdir):
            ErrorMessage.throw(ExitCodes.FILE_NOT_FOUND, confdir)

        utilities.cp_f(os.path.join(self.template_path, "*.rts"), specsdir)
        utilities.cp_f(os.path.join(self.fmilib_root, "*.rts"), specsdir)

        with open(os.path.join(self.template_path, "sut.confinc"), "r") as input_file:
            with open(os.path.join(confdir, "sut.confinc"), "w") as output_file:
                output_file.writelines(utilities.sed_g("\@FMI2_LIB\@", "${RTT_TESTCONTEXT}/" + self.fmilib_rel_path, input_file))
                if self.is_simulation:
                    output_file.write("\n// Added by " + self.get_tool_description() + "\n")
                    output_file.write("CFLAGS ; -DDISABLE_STIMULATION\n")
                if self.is_simulation or self.is_sut:
                    output_file.write("\n// Block socket output for Sim/SUT [" + self.get_tool_description() + "]\n")
                    output_file.write("CFLAGS ; -DRTT_BLOCK_SIGNAL_SOCKET\n")

    def __create_interface_library(self):
        """
        This method copies the required template files to the test context and
        automatically triggers the code generation for the concrete FMI XML
        interface file. Both parts together results in a complete FMU library
        that can be compiles and packages.
        :return: None
        """
        if not os.path.exists(self.fmilib_root):
            os.mkdir(self.fmilib_root)
        if not os.path.isdir(self.fmilib_root):
            ErrorMessage.throw(ExitCodes.FILE_NOT_FOUND, self.fmilib_root)

        #print "DO: cp_f()"
        utilities.cp_f(os.path.join(self.template_path, "*.c"), self.fmilib_root)
        utilities.cp_f(os.path.join(self.template_path, "*.h"), self.fmilib_root)

        # Finally copy the Makefile.template
        model_identifier = self.get_fmi_model_name()

        #print "DO: open()"
        with open(os.path.join(self.template_path, "Makefile.template"), "r") as input_file:
            with open(os.path.join(self.fmilib_root, "Makefile"), "w") as output_file:
                output_file.writelines(utilities.sed_g("\@FMI2_MODEL_IDENTIFIER\@", model_identifier, input_file))

        fmi2lib_path = os.path.join(self.toolbindir, "rtt-mbt-fmi2rts")
        print "DO: execute(fmi2lib_path = {0}, fmilib_root={1}, model={2})".format(fmi2lib_path, self.fmilib_root, self.fmi_model_description_path)
        #with open(self.fmi_model_description_path) as new_file:
        #    for line in new_file:
        #        print line
        utilities.execute(fmi2lib_path, cwd=self.fmilib_root, args=[self.fmi_model_description_path])
        print "DONE."

    def __build_interface_library(self):
        """
        This method relies on the Makefile, which was automatically generated by
        __create_interface_library(). Here only the "make" command is issued and
        the library is being built.
        :return: Boolean stating if "make" succeeded.
        """
        return_code = utilities.execute("make", cwd=self.fmilib_root, args=["-f", "Makefile"])
        if return_code != 0:
            ErrorMessage.throw(ExitCodes.EXTERNAL_TOOL_ERROR, "make", return_code)
            return False
        return True

    def build_fmu(self, testprocedure):
        """
        Constructs an FMU from a given test procedure.
        :param testprocedure: Path to the test procedure starting from RTT_TESTCONTEXT.
        :return: path to the FMU.
        """

        rtt_test_case = os.path.join(self.testcontext, testprocedure, "src", "rtt-test-case")
        rebuild = False
        if not os.path.exists(rtt_test_case):
            rebuild = True

        if not rebuild:
            mtime_xml = os.path.getmtime(self.fmi_model_description_path)
            mtime_testproc = os.path.getmtime(rtt_test_case)
            if mtime_testproc < mtime_xml:
                rebuild = True

        rtt6 = RTT6(testprocedure)
        if rebuild:
            sys.stderr.write("## DO COMPILE TP: '{0}'\n".format(testprocedure))
            if rtt6.compile(self.force) != 0:
                ErrorMessage.throw(ExitCodes.TEST_PROCEDURE_NOT_EXISTS, testprocedure)

        fmu_root = tempfile.mkdtemp(suffix=".fmutmp", dir=self.fmilib_root)
        fmu_doc = os.path.join(fmu_root, "documentation")
        fmu_bin = os.path.join(fmu_root, "binaries")
        fmu_src = os.path.join(fmu_root, "sources")
        fmu_res = os.path.join(fmu_root, "resources")
        fmu_bin_platform = os.path.join(fmu_bin, self.__get_platform())

        utilities.mkdir_p(fmu_bin_platform)
        utilities.cp_f(self.fmilib_path, fmu_bin_platform)

        utilities.mkdir_p(fmu_res)
        rtt6_testprocedure = os.path.join(rtt6.component_name, rtt6.procedure_name)
        self.__build_fmu_testproc(fmu_res, rtt6_testprocedure)

        # If the FMU should also contain sources, enable this code:
        # self.__copy_fmu_sources(fmu_src)

        utilities.cp_f(self.fmi_model_description_path, os.path.join(fmu_root, "modelDescription.xml"))

        if rtt6.component_name.startswith("RTT_"):
            mbt_component_name = rtt6.component_name[4:]
            mbt_testprocedure = os.path.join(mbt_component_name, rtt6.procedure_name)
            mbtdir = os.path.join(self.testcontext, mbt_testprocedure)
            if os.path.exists(mbtdir):
                mbtlogdir = os.path.join(mbtdir, "log", "*.html")
                utilities.mkdir_p(fmu_doc)
                utilities.cp_f(mbtlogdir, fmu_doc)

            signals_json = os.path.join(self.testcontext, mbt_testprocedure, "model", "signals.json")
            if os.path.exists(signals_json):
                self.__add_default_experiment(os.path.join(fmu_root, "modelDescription.xml"), signals_json)

        zipfilename = os.path.join(self.testcontext, testprocedure, self.get_fmi_model_name() + ".fmu")
        self.__create_zip(zipfilename, fmu_root + os.path.sep)
        utilities.rm_f(fmu_root)
        return zipfilename

    def __copy_fmu_sources(self, fmu_src):
        """
        The FMU might also contain the files to compile the FMU for each platform.
        This method copies the files to the specified target directory (named "sources").
        Still the files must also be listed in the modelDescription.xml file.
        :param fmu_src: the sources directory of the FMU archive
        :return: None
        """
        utilities.mkdir_p(fmu_src)
        utilities.cp_f(os.path.join(self.fmilib_root, "*.c"), fmu_src)

        matches = glob.glob(os.path.join(self.fmilib_root, "*.h"))
        for source in matches:
            if (not(source.endswith(os.sep + "fmi2TypesPlatform.h"))
               and not(source.endswith(os.sep + "fmi2FunctionTypes.h"))
               and not(source.endswith(os.sep + "fmi2Functions.h"))):
                    shutil.copy(source, fmu_src)

    def __get_platform(self):
        """
        Creates the directory name for the platform. Currently only 64 bit
        platforms as supported, but this should be extendedn
        :return: the name of the platform according to FMU standard, e.g. linux64.
        """
        arch = "64"
        if sys.platform.startswith('win'):
            return "win" + arch
        elif sys.platform.startswith('mingw'):
            return "win" + arch
        elif sys.platform.startswith('linux'):
            return "linux" + arch
        elif sys.platform.startswith('darwin'):
            return "darwin" + arch
        else:
            return sys.platform + arch

    def __get_sharedlib_extension(self):
        if sys.platform.startswith('win'):
            return ".dll"
        elif sys.platform.startswith('mingw'):
            return ".dll" + arch
        elif sys.platform.startswith('linux'):
            return ".so"
        elif sys.platform.startswith('darwin'):
            return ".dylib"
        else:
            return ".so"

    def __build_fmu_testproc(self, resourcedir, testprocedure):
        """
        Creates a testproc.conf file in the resources directory of the FMU.
        This file will be used by the FMU library to start the rtt-test-case
        executable for test execution.
        :param resourcedir: the name of the directory, where the file should be placed.
        :param testprocedure: the make of the test procedure relative to RTT_TESTCONTEXT.
        :return: None
        """
        runtest = utilities.which("rtt-launch-test.py")
        if not runtest:
            runtest = os.path.join(os.environ['RTTDIR'], "bin", "rtt-launch-test.py")
        testproc_path = os.path.join(self.testcontext, testprocedure)
        context = self.testcontext
        if sys.platform.startswith('win') and " " in context:
            context = '"' + context + '"'

        with open(os.path.join(resourcedir, "testproc.conf"), "wb") as testproc:
            testproc.write('HOSTNAME={0}\n'.format(socket.gethostname()))
            testproc.write('TESTPROCEDURE="{0}"\n'.format(testproc_path))
            testproc.write('RTT_TESTCONTEXT={0}\n'.format(context))
            testproc.write('CMD_RUN={0} {1}\n'.format(runtest, testprocedure))

    def __create_zip(self, output_filename, source_dir):
        """
        Creates a ZIP file from a given source directory.
        :param output_filename: the name of the zip file
        :param source_dir: the directory to be zipped.
        :return: None
        """
        relroot = os.path.abspath(source_dir)
        if os.path.exists(output_filename):
            utilities.rm_f(output_filename)

        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename): # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)
