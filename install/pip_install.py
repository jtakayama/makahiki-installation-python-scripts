import os
import subprocess
import shlex
import re
import string
import datetime

def termination_string():
    """
    Gets the current system time and appends it to a termination notice.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    end_time = "Script exiting at %s\n" % time
    return end_time
    
def run(logfile):
    """
    Runs "pip install -r requirements.txt", logging output to the logfile.
    Parameters: 
        1. logfile: A file to log output to.
    """
    # Write first line to file
    firstline = "pip installation script"
    logfile.write(firstline)
    print firstline
    
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    start_time = "Script started at %s\n" % time
    logfile.write(start_time)
    print start_time
    try:
        USER_HOME = subprocess.check_output(["echo $HOME"], stderr=subprocess.STDOUT, shell=True) 
        # Remove newline from expected "/home/<username>\n"
        USER_HOME = USER_HOME[:-1]
        USER_PROJECT_HOME = USER_HOME + "/makahiki"
        # cd to makahiki directory so pip can find the requirements.txt file
        os.chdir(USER_PROJECT_HOME)
        pip_output = subprocess.check_output(["pip install -r requirements.txt"], stderr=subprocess.STDOUT, shell=True)
        logfile.write(pip_output)
        print(pip_output)
        # pip produces a lot of output. Clear the buffer before reading in anything else.
        logfile.flush()
        os.fsync(logfile)
        # Print a closing message
        closing = "\npip install script completed successfully.\n"
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile
    except subprocess.CalledProcessError as cpe:
        logfile.write("CalledProcessError: ")
        print "CalledProcessError: "
        logfile.write(cpe.output)
        print cpe.output
        logfile.write("Warning: pip requirements installation did not complete successfully.\n")
        print "Warning: pip requirements installation did not complete successfully.\n"
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile 
