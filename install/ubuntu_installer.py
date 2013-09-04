#!/usr/bin/python
import sys
import os
import datetime
import datestring_functions
import ubuntu.dependency_ubuntu
import pip_install
import run_update_instance
import run_initialize_instance
import cleanup

def logfile_open(scripttype):
    """
    Returns an open logfile with a timestamp. It is left to the 
    calling function to write to the file and close it.
    
    This function will return None if an IOError occurs while 
    opening the file.
    
    Parameters:
        1. scripttype: A string describing the installation script
           that is being run.
    """
    # Build file path to logs directory based on location of this file
    runpath = os.path.dirname(os.path.realpath(__file__))
    pathdirs = runpath.split(os.sep)
    assembled_path = ""
    i = 0
    # Assume the last part is the filename
    while i < len(pathdirs):
        if i == 0:
            assembled_path = pathdirs[i]
        else:
            assembled_path = assembled_path + os.sep + pathdirs[i]
        i = i + 1
    
    logsdir = assembled_path + os.sep + "logs"
    prefix = "install_" + scripttype + "_"
    dt = datetime.datetime
    date_suffix = "null"
    logfile = None
    try:
        date_suffix = datestring_functions.datestring(dt)
        logfile_path = logsdir + os.sep + prefix + date_suffix + ".log"
        try:
            logfile = open(logfile_path, 'w')
        except IOError as ioe:
            print "IOError:\n %s" % ioe
            print "Could not open logfile at %s for writing." % logfile_path
            print "Script will terminate."
            logfile = None
    except ValueError as ve:
        print "ValueError:\n %s" % ve
        print "Bad datetime object, could not generate logfile name."
        print "Script will terminate."
        logfile = None
    return logfile

def scriptrunner(scripttype, logfile, arch="no_arch"):
    """
    Chooses and runs an installation script, and supplies the 
    logfile that the script will write its output to.
    
    Though not all scripts are OS-dependent, the "arch" 
    parameter is used to determine if the system is supported.
    
    Parameters:
        1. scripttype: The installation script that is being run. 
           Supported values: 
           "dependencies", "cleanup", "pip", "initialize_instance", "update_instance"
        2. logfile: The log file to pass to the installation script.
        3. arch: Architecture. Ubuntu is supported for x86 and x64 architectures.
           The "dependencies" option requires x86 or x64 to be specified.
           The default value is "no_arch".
    """
    if (arch == "x86" or arch == "x64" or arch == "no_arch"):
        if scripttype == "dependencies" and (arch == "x86" or arch == "x64"):
            logfile = ubuntu.dependency_ubuntu.run(arch, logfile)
        elif scripttype == "dependencies" and arch == "no_arch":
            logfile.write("No architecture specified for dependencies.")
            logfile.write("Script could not be completed.\n")
            print "No architecture specified for dependencies."
            print "Script could not be completed.\n"
        elif (scripttype in ["cleanup","pip","initialize_instance","update_instance"]):
            if (arch == "x86" or arch == "x64"):
                print ("%s script is x86 and x64-compatible." % scripttype)
            # Run one of the architecture-independent scripts
            if scripttype == "cleanup":
                logfile = cleanup.run(logfile)
            elif scripttype == "pip":
                logfile = pip_install.run(logfile)
            elif scripttype == "initialize_instance":
                logfile = run_initialize_instance.run(logfile)
            elif scripttype == "update_instance":
                logfile = run_update_instance.run(logfile)
        else:
            logfile.write("Error: ubuntu_installer.py invoked with invalid command: %s\n" % scripttype)
            print "Error: ubuntu_installer.py invoked with invalid command: %s\n" % scripttype
    else:
        logfile.write("Unsupported architecture for Ubuntu: %s\n" % arch)
        logfile.write("Script could not be completed.\n")
        print "Unsupported architecture for Ubuntu: %s\n" % arch
        print "Script could not be completed.\n"
    # After the function is done, return the logfile.
    return logfile

def main():
    number_of_args = len(sys.argv)
    if ((number_of_args != 2 and number_of_args != 4) or (number_of_args == 4 and sys.argv[2] != "--arch")):
        print "Usage: ubuntu_installer.py < --dependencies --arch < x86 | x64 > | --cleanup | --pip | --initialize_instance | --update_instance >"
        print "--dependencies: Install Makahiki dependencies (software packages)."
        print "  This is the only command that requires --arch to be specified."
        print "--cleanup: Remove archives and other files downloaded by Makahiki scripts."
        print "--pip: Install Makahiki local dependencies using pip."
        print "--initialize_instance: Initialize the Makahiki installation."
        print "--update_instance: Update the Makahiki installation."
        print "--arch: Architecture. This script supports x86 and x64 for Ubuntu Linux."
    else:
        if number_of_args == 4:
            args = sys.argv[1:]
            scripttype = args[0].strip()[2:]
            arch = args[2].strip()
            logfile = logfile_open(scripttype)
            if logfile == None:
                exit(1)
            else:
                scriptrunner(scripttype,logfile,arch)
                logfile.close()
        elif number_of_args == 2:
            args = sys.argv[1:]
            scripttype = args[0].strip()[2:]
            logfile = logfile_open(scripttype)
            if logfile == None:
                exit(1)
            else:
                scriptrunner(scripttype,logfile)
                logfile.close()

if __name__ == '__main__':
    main()