#!/usr/bin/python2.6

import sys
import os
import datetime
import datestring_functions
import redhat.scl_install

# NOTE:
# This script is meant to be run under Python 2.6.6 (the default version on 
# RHEL 6 x64) in order to install Python 2.7.3.

def logfile_open(scripttype):
    """
    Returns an open logfile with a timestamp. It is left to the 
    calling function to write to the file and close it.
    
    This function will terminate the calling function if an IOError 
    occurs while opening the file.
    
    Parameters:
        1. scripttype: A string describing the installation script
           that is being run.
    """
    rundir = os.getcwd()
    logsdir = "/install/logs/"
    prefix = "install_" + scripttype + "_"
    dt = datetime.datetime
    date_suffix = "null"
    logfile = None
    try:
        date_suffix = datestring_functions.datestring(dt)
        # Assumes rundir is not terminated with a "/"
        logfile_path = rundir + logsdir + prefix + date_suffix + ".log"
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

def main():
    scripttype = "sclinstall"
    logfile = logfile_open("sclinstall")
    logfile = redhat.scl_install.run(logfile)
    logfile.close()

if __name__ == '__main__':
    main()
