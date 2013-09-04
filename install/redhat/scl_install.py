import datetime
import commands
import re
import os

def termination_string():
    """
    Gets the current system time and appends it to a termination notice.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    end_time = "Script exiting at %s\n" % time
    return end_time

def run_command(command, logfile):
    """
    Executes <command> and logs its output to <logfile>.
    Note that this does not log the console output of commands.
    
    Parameters:
       1. command: The command to be executed.
       2. logfile: The logfile to write output to.
       
    Returns the tuple "result."
    result[0] is True if the installation succeeded and False if it did not.
    result[1] is a reference to the logfile passed in as parameter 2.
    """
    success = False
    logfile.write("Attempting: " + command + "\n")
    print "Attempting: " + command + "\n"
    try:
        # Execute command - returns a CalledProcessError if it fails
        tuple = commands.getstatusoutput(command)
        status = tuple[0]
        output = tuple[1]
        # Print output line by line
        output2 = output.split("\n")
        for line in output2:
            logfile.write(line + "\n")
            print line
        # Check result
        if status == 0:
            logfile.write("Operation successful:\n%s\n" % command)
            print "Operation successful:\n%s\n" % command
            success = True
    except OSError as ose:
        logfile.write("OSError: ")
        print "OSError: "
        oserror_output = " errno: %s\n filename: %s\n strerror: %s\n" % (ose.errno, ose.filename, ose.strerror) 
        logfile.write(oserror_output)
        print oserror_output
        closing = "\nOperation failed:\n%s" % command
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        success = False

    # Return result tuple
    result = [success, logfile]
    return result

def run(logfile):
    """
    Installs Python 2.7.3 from Redhat Software Collections.
    
    Parameters:
        1.    logfile: The logfile to write output to. 
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    start_time = "Script starting at %s\n" % time
    logfile.write(start_time)
    print start_time
        
    download_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep + "download")
    os.chdir(download_dir)
    
    # Install wget
    result = run_command("yum install -y wget", logfile)
    success = result[0]
    logfile = result[1]
    if not success:
        return logfile
    
    # Retrieve the repo file
    repo_url = "http://people.redhat.com/bkabrda/scl_python27.repo"
    repoadd = "The repository at %s will be added to the system.\n" % repo_url
    logfile.write(repoadd)
    print repoadd
    result = run_command("wget %s" % repo_url, logfile)
    success = result[0]
    logfile = result[1]
    if not success:
        return logfile
    
    # Copy the repo file to the system repos directory
    result = run_command("cp ./scl_python27.repo /etc/yum.repos.d/scl_python27.repo", logfile)
    success = result[0]
    logfile = result[1]
    if not success:
        return logfile
    
    # Clean up the .repo file when done.
    result = run_command("rm ./scl_python27.repo", logfile)
    success = result[0]
    logfile = result[1]
    if not success:
        return logfile
    
    # Install Python 2.7.3 from SCL collections
    logfile.write("Python 2.7.3 will be installed from SCL.\n")
    print "Python 2.7.3 will be installed from SCL.\n"
    result = run_command("yum install -y python27", logfile)
    success = result[0]
    logfile = result[1]
    if not success:
        return logfile
    
    # After this, the user must run "scl enable python27 bash"
    # manually.
    
    # Print a closing message
    closing = "\nPython 2.7.3 SCL installation script has completed.\n"
    logfile.write(closing)
    print closing
    end_time = termination_string()
    logfile.write(end_time)
    print end_time
    return logfile