import os
import subprocess
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
    Runs the makahiki/makahiki/scripts/update_instance.py
    script and logs the output to a file.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    start_time = "Makahiki instance update script started at %s\n" % time
    logfile.write(start_time)
    print start_time

    try:
        USER_HOME = subprocess.check_output(["echo $HOME"], stderr=subprocess.STDOUT, shell=True) 
        # Remove newline from expected "/home/<username>\n"
        USER_HOME = USER_HOME[:-1]
        USER_PROJECT_HOME = USER_HOME + os.sep + "makahiki"
        # cd to makahiki directory so pip can find the requirements.txt file
        os.chdir(USER_PROJECT_HOME)
        update_output = subprocess.check_output(["python ./makahiki/scripts/update_instance.py"], stderr=subprocess.STDOUT, shell=True)
        logfile.write(update_output)
        print(update_output)
        # Clear the buffer.
        logfile.flush()
        os.fsync(logfile)
        # Print a closing message
        closing = "\nMakahiki instance update script has completed.\n"
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
        logfile.write("Warning: Makahiki instance update did not complete successfully.\n")
        print "Warning: Makahiki instance update did not complete successfully.\n"
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile 
    except OSError as ose:
        logfile.write("OSError: ")
        print "OSError: "
        oserror_output = " errno: %s\n filename: %s\n strerror: %s\n" % (ose.errno, ose.filename, ose.strerror) 
        logfile.write(oserror_output)
        print oserror_output
        logfile.write("Warning: Makahiki instance update did not complete successfully.\n")
        print "Warning: Makahiki instance update did not complete successfully.\n"
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile
