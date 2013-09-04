import re
import os
import shlex
import datetime
import commands

# This script needs to be run with sudo. Since this causes the 
# shell to default back to the default version of Python
# (2.6.6 on RHEL 6 / CentOS 6), the script uses the "commands" 
# module to replace functionality missing from 2.6.6's version 
# of the subprocess module.

def rpm_check(packagename):
    """
    Uses "rpm -q <packagename>" to check if a package is installed.
    It does not check the version. Returns True if it is installed, and 
    False if it is not.
    """
    escaped_packagename = re.escape(packagename)
    rpm_regex = re.compile("(%s)(.)+(\.)(.)+" % escaped_packagename)
    result = False
    try:
        tuple = commands.getstatusoutput("rpm -q %s" % packagename)
        status = tuple[0]
        output = tuple[1]
        if status == 0:
            output2 = output.split("\n")
            if rpm_regex.match(output2[0]):
                result = True
            else:
                result = False
        elif status == 1:
            result = False
    # Assume not installed
    except OSError as ose:
        result = False
    except CalledProcessError as cpe:
        result = False
    return result

def postgresql91_repocheck():
    """
    Checks if the pgdg-redhat91-9.1-5.noarch.rpm repo (pgdg91) is installed.
    Returns True if it is listed by yum repolist, and False if it not.
    """
    repo_match = False
    repo_shortname = re.compile("(pgdg91)(.)*")
    try:
        tuple = commands.getstatusoutput("yum repolist | grep pgdg91")
        status = tuple[0]
        output = tuple[1]
        output2 = output.split("\n")
        for line in output2:
            linematch = repo_shortname.match(line)
            if linematch:
                repo_match = True
                break
    # Assume not installed
    except OSError as ose:
        repo_match = False
    return repo_match

def libmemcached053_check():
    """
    Checks for the existence of the libmemcached.so library in 
    /usr/local/lib, which is where this script installs 
    libmemcached-0.53 after building it.
    """
    result = False
    try:
        # The libmemcached-0.53 install is not an rpm and must be checked another way
        libmemcached053_installed = os.stat("/usr/local/lib/libmemcached.so")
        if libmemcached053_installed:
            result = True
    except OSError as libmemcached_error:
        result = False
    return result

def termination_string():
    """
    Gets the current system time and appends it to a termination notice.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    end_time = "Script exiting at %s\n" % time
    return end_time

def current_time():
    """
    Returns the current system time as a string.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    return time

def yum_install(packagename, logfile):
    """
    Installs <packagename> with "yum install -y <packagename>" and then 
    checks whether or not the package installed correctly. Output is logged to 
    the logfile.
    
    Parameters:
        1. packagename: A string with the name of the package to be installed.
        2. logfile: The file to write output to.
    Returns a tuple, result:
    result[0] is True if the installation succeeded and False if it did not.
    result[1] is a reference to the logfile passed in as parameter 2.
    """
    success = False
    logfile.write("%s will be installed.\n" % packagename)
    print ("%s will be installed.\n" % packagename)
    logfile.write("yum install -y %s\n" % packagename)
    print "yum install -y %s\n" % packagename
    try:
        tuple = commands.getstatusoutput("yum install -y %s" % packagename)
        status = tuple[0]
        output = tuple[1]
        # Print output line by line
        output2 = output.split("\n")
        for line in output2:
            logfile.write(line + "\n")
            print line
        # Check if RPM was installed
        is_installed = rpm_check(packagename)
        if is_installed:
            logfile.write("%s installed successfully.\n" % packagename)
            print "%s installed successfully.\n" % packagename
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
            success = True
        else:
            logfile.write("Package %s failed to install.\n" % packagename)
            print "Package %s failed to install.\n" % packagename
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            success = False
        return [success, logfile]
    except CalledProcessError as cpe:
        # Print and log the error message
        logfile.write("CalledProcessError: ")
        print "CalledProcessError: "
        logfile.write(cpe.output)
        print cpe.output
        closing = "\nPackage %s failed to install.\n" % packagename
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        success = False
        return [success, logfile]
    except OSError as ose:
        logfile.write("OSError: ")
        print "OSError: "
        oserror_output = " errno: %s\n filename: %s\n strerror: %s\n" % (ose.errno, ose.filename, ose.strerror) 
        logfile.write(oserror_output)
        print oserror_output
        closing = "\nPackage %s failed to install.\n" % command
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        success = False
        return [success, logfile] 

def run_command(command, logfile, message="Operation"):
    """
    Executes <command> and logs its output to <logfile> with <message>.
    Note that this does not log the console output of commands.
    
    Parameters:
       1. command: The command to be executed.
       2. logfile: The logfile to write output to.
       3. message: The custom message. The output is: 
          Output of success: <message> successful: <command>
          Output of failure: <message> failed: <command>
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
            logfile.write("%s successful:\n%s\n" % (message, command))
            print "%s successful:\n%s\n" % (message, command)
            success = True
    except OSError as ose:
        logfile.write("OSError: ")
        print "OSError: "
        oserror_output = " errno: %s\n filename: %s\n strerror: %s\n" % (ose.errno, ose.filename, ose.strerror) 
        logfile.write(oserror_output)
        print oserror_output
        closing = "\n%s failed:\n%s" % (message, command)
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        success = False

    # Return result tuple
    result = [success, logfile]
    return result

def run(arch, logfile):
    """
    Installs and configures some Makahiki dependencies by issuing 
    system commands. Writes its output to a logfile while printing 
    it to the console.
    
    The target OS is Red Hat Enterprise Linux (RHEL). x64 RHEL is supported.
    """
    pythonpath = "/opt/rh/python27/root/usr/bin"
    
    # Write first line to file
    firstline = "Makahiki installation script for Red Hat Enterprise Linux %s" % arch
    logfile.write(firstline)
    print firstline
    
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    start_time = "Script started at %s\n" % time
    logfile.write(start_time)
    print start_time
    
    # Confirm that the user wants to continue.
    logfile.write("This script will add PostgreSQL's pgdg91 repository to the system.\n")
    print "This script will add PostgreSQL's pgdg91 repository to the system.\n"
    logfile.write("This script will uninstall libmemcached if it is installed.\n")
    print "This script will uninstall libmemcached if it is installed.\n"
    dependencies_list = "This script will install these packages and their dependencies:\n\
         All packages in groupinstall \"Development tools\",\n\
         git,\n\
         gcc,\n\
         python-imaging,\n\
         python-devel,\n\
         libjpeg-devel,\n\
         zlib-devel,\n\
         postgresql91-server,\n\
         postgresql91-contrib,\n\
         postgresql91-devel,\n\
         memcached,\n\
         libmemcached-0.53\n"
    logfile.write(dependencies_list)
    print dependencies_list
    value = raw_input("Do you wish to continue (Y/n)? ")
    while value != "Y" and value != "n":
        logfile.write("Invalid option %s\n" % value)
        print "Invalid option %s\n" % value
        value = raw_input("Do you wish to continue (Y/n)? ")
    if value == "n":
        logfile.write("Do you wish to continue (Y/n)? %s\n" % value)
        logfile.write("Operation cancelled.")
        print "Operation cancelled.\n"
        return logfile
    elif value =="Y":
        logfile.write("Do you wish to continue (Y/n)? %s\n" % value)
        logfile.write("Starting dependency installation for RHEL 6 %s.\nChecking for dependencies...\n" % arch)
        print "Starting dependency installation for RHEL 6 %s.\nChecking for dependencies...\n" % arch
        
        # Boolean variables for each dependency
        git_installed = rpm_check("git")
        gcc_installed = rpm_check("gcc")
        python_imaging_installed = rpm_check("python-imaging")
        python_devel_installed = rpm_check("python-devel")
        libjpeg_devel_installed = rpm_check("libjpeg-turbo-devel")
        postgresql91_repo = postgresql91_repocheck()
        postgresql91_server_installed = rpm_check("postgresql91-server")
        postgresql91_contrib_installed = rpm_check("postgresql91-contrib")
        postgresql91devel_installed = rpm_check("postgresql91-devel")
        memcached_installed = rpm_check("memcached")
        libmemcached_installed = rpm_check("libmemcached")
        libmemcached053_installed = libmemcached053_check()
        zlib_devel_installed = rpm_check("zlib-devel")
        
        # Groupinstall of "Development tools" (the script does not check if its components are installed or not)
        time = current_time()
        logfile.write("Development tools groupinstall started at %s.\n" % time)
        print "Development tools groupinstall started at %s.\n" % time
        groupinstall_command = "yum groupinstall -y \"Development tools\""
        groupinstall_result = run_command(groupinstall_command, logfile, "Groupinstall of \"Development tools\"")
        success = groupinstall_result[0]
        logfile = groupinstall_result[1]
        if not success:
            return logfile
        else:
            time = current_time()
            logfile.write("Development tools groupinstall finished at %s.\n" % time)
            print "Development tools groupinstall finished at %s.\n" % time
        
        # git
        if git_installed:
            logfile.write("git is already installed.\n")
            print "git is already installed.\n" 
        else:
            time = current_time()
            logfile.write("git installation started at %s.\n" % time)
            print "git installation started at %s.\n" % time
            git_result = yum_install("git", logfile)
            success = git_result[0]
            logfile = git_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("git installation finished at %s.\n" % time)
                print "git installation finished at %s.\n" % time
                
        # gcc
        if gcc_installed:
            logfile.write("gcc is already installed.\n")
            print "gcc is already installed.\n" 
        else:
            time = current_time()
            logfile.write("gcc installation started at %s.\n" % time)
            print "gcc installation started at %s.\n" % time
            gcc_result = yum_install("gcc", logfile)
            success = gcc_result[0]
            logfile = gcc_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("gcc installation finished at %s.\n" % time)
                print "gcc installation finished at %s.\n" % time
    
        logfile.write("Beginning installation of Python Imaging Library components python-imaging, python-devel, and libjpeg-devel.\n")
        print "Beginning installation of Python Imaging Library components python-imaging, python-devel, and libjpeg-devel.\n"
            
        # python-imaging    
        if python_imaging_installed:
            logfile.write("python-imaging is already installed.\n")
            print "python-imaging is already installed.\n" 
        else:
            time = current_time()
            logfile.write("python-imaging installation started at %s.\n" % time)
            print "python-imaging installation started at %s.\n" % time
            python_imaging_result = yum_install("python-imaging", logfile)
            success = python_imaging_result[0]
            logfile = python_imaging_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("python-imaging installation finished at %s.\n" % time)
                print "python-imaging installation finished at %s.\n" % time
    
        # postgresql91-server
        if python_devel_installed:
            logfile.write("python-devel is already installed.\n")
            print "python-devel is already installed.\n" 
        else:
            time = current_time()
            logfile.write("python-devel installation started at %s.\n" % time)
            print "python-devel installation started at %s.\n" % time
            python_devel_result = yum_install("python-devel", logfile)
            success = python_devel_result[0]
            logfile = python_devel_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("python-devel installation finished at %s.\n" % time)
                print "python-devel installation finished at %s.\n" % time
            
        # libjpeg-devel
        if libjpeg_devel_installed:
            logfile.write("libjpeg-devel (libjpeg-turbo-devel) is already installed.\n")
            print "libjpeg-devel (libjpeg-turbo-devel) is already installed.\n" 
        else:
            time = current_time()
            logfile.write("libjpeg-devel (libjpeg-turbo-devel) installation started at %s.\n" % time)
            print "libjpeg-devel (libjpeg-turbo-devel) installation started at %s.\n" % time
            libjpeg_devel_result = yum_install("libjpeg-turbo-devel", logfile)
            success = libjpeg_devel_result[0]
            logfile = libjpeg_devel_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("libjpeg-devel (libjpeg-turbo-devel) installation finished at %s.\n" % time)
                print "libjpeg-devel (libjpeg-turbo-devel) installation finished at %s.\n" % time
    
        # zlib-devel
        if zlib_devel_installed:
            logfile.write("zlib-devel is already installed.\n")
            print "zlib-devel is already installed.\n"   
        else:
            time = current_time()
            logfile.write("zlib-devel installation started at %s.\n" % time)
            print "zlib-devel installation started at %s.\n" % time
            zlib_devel_result = yum_install("zlib-devel", logfile)
            success = zlib_devel_result[0]
            logfile = zlib_devel_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("zlib-devel installation finished at %s.\n" % time)
                print "zlib-devel installation finished at %s.\n" % time
                
        # Check locations of shared libraries
        time = current_time()
        logfile.write("Checking for Python Imaging Library shared libraries: started at%s\n" % time)
        print "Checking for Python Imaging Library shared libraries: started at %s\n" % time
        # libjpeg.so
        if arch == "x86":
            try:
                libjpeg_stat = os.stat("/usr/lib/libjpeg.so")
                if libjpeg_stat:
                    output1 = "Found libjpeg.so at /usr/lib/libjpeg.so\n"
                    logfile.write(output1)
                    print output1
            except OSError as libjpeg_error:
                error1 = "Error: Could not find libjpeg.so in /usr/lib.\n"
                error2 = "Python Imaging Library-related packages may not have installed properly.\n"
                logfile.write(error1)
                logfile.write(error2)
                print error1
                print error2
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        elif arch == "x64":
            try:
                libjpeg_stat = os.stat("/usr/lib64/libjpeg.so")
                if libjpeg_stat:
                    output2 = "Found libjpeg.so at /usr/lib64/libjpeg.so\n"
                    output3 = "Symbolic link will be created: /usr/lib/libjpeg.so --> /usr/lib64/libjpeg.so\n"
                    output4 = "ln -s /usr/lib64/libjpeg.so /usr/lib/libjpeg.so\n"
                    logfile.write(output2)
                    logfile.write(output3)
                    logfile.write(output4)
                    print output2
                    print output3
                    print output4
                    libjpeg_tuple = commands.getstatusoutput("ln -s /usr/lib64/libjpeg.so /usr/lib/libjpeg.so")
                    status = libjpeg_tuple[0]
                    if status != 0:
                        error1 = "Error: Could not create symbolic link: /usr/lib/libjpeg.so --> /usr/lib/64/libjpeg.so\n"
                        logfile.write(error1)
                        print error1
                        end_time = termination_string()
                        logfile.write(end_time)
                        print end_time
                        return logfile 
            except OSError as libjpeg_error:
                error1 = "Error: Could not find libjpeg.so in /usr/lib64.\n"
                error2 = "Python Imaging Library-related packages may not have installed properly.\n"
                logfile.write(error1)
                logfile.write(error2)
                print error1
                print error2
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        
        # libz.so
        if arch == "x86":
            try:
                libjpeg_stat = os.stat("/usr/lib/libz.so")
                if libjpeg_stat:
                    output1 = "Found libz.so at /usr/lib/libz.so\n"
                    logfile.write(output1)
                    print output1
            except OSError as libz_error:
                error1 = "Error: Could not find libz.so in /usr/lib.\n"
                error2 = "Python Imaging Library-related packages may not have installed properly.\n"
                logfile.write(error1)
                logfile.write(error2)
                print error1
                print error2
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        elif arch == "x64":
            try:
                libz_stat = os.stat("/usr/lib64/libz.so")
                if libz_stat:
                    output2 = "Found libz.so at /usr/lib64/libz.so\n"
                    output3 = "Symbolic link will be created: /usr/lib/libz.so --> /usr/lib/64/libz.so\n"
                    output4 = "ln -s /usr/lib64/libz.so /usr/lib/libz.so\n"
                    logfile.write(output2)
                    logfile.write(output3)
                    logfile.write(output4)
                    print output2
                    print output3
                    print output4
                    libz_tuple = commands.getstatusoutput("ln -s /usr/lib64/libz.so /usr/lib/libz.so")
                    status = libz_tuple[0]
                    if status != 0:
                        error1 = "Error: Could not create symbolic link: /usr/lib/libz.so --> /usr/lib/64/libz.so\n"
                        logfile.write(error1)
                        print error1
                        end_time = termination_string()
                        logfile.write(end_time)
                        print end_time
                        return logfile 
            except OSError as libz_error:
                error1 = "Error: Could not find libz.so in /lib64.\n"
                error2 = "Python Imaging Library-related packages may not have installed properly.\n"
                logfile.write(error1)
                logfile.write(error2)
                print error1
                print error2
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        
        time = current_time()
        logfile.write("Checking for Python Imaging Library shared libraries: finished at%s\n" % time)
        print "Checking for Python Imaging Library shared libraries: finished at %s\n" % time
        logfile.write("Installation of Python Imaging Library components is complete.\n")
        print "Installation of Python Imaging Library components is complete.\n"
        
        # memcached
        if memcached_installed:
            logfile.write("memcached is already installed.\n")
            print "memcached is already installed.\n"   
        else:
            time = current_time()
            logfile.write("memcached installation started at %s.\n" % time)
            print "memcached installation started at %s.\n" % time
            memcached_result = yum_install("memcached", logfile)
            success = memcached_result[0]
            logfile = memcached_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("memcached installation finished at %s.\n" % time)
                print "memcached installation finished at %s.\n" % time
        
        # Beginning of libmemcached-0.53 installation code.
        if libmemcached053_installed:
            logfile.write("libmemcached alternate installation found in /usr/local/lib\n")
            logfile.write("The user should check that this alternate installation is libmemcached-0.53.\n")
            logfile.write("libmemcached-0.53 will not be installed. Continuing...\n")
            print "libmemcached alternate installation found in /usr/local/lib\n"
            print "The user should check that this alternate installation is libmemcached-0.53.\n"
            print "libmemcached-0.53 will not be installed. Continuing...\n"
        elif libmemcached053_installed is False:
            if libmemcached_installed:
                time = current_time()
                logfile.write("libmemcached removal started at %s.\n" % time)
                print "libmemcached removal started at %s.\n" % time
                logfile.write("libmemcached will be removed.\n")
                print "libmemcached will be removed.\n"
                remove_libmemcached_command = "yum remove -y libmemcached"
                logfile.write(remove_libmemcached_command + "\n")
                print remove_libmemcached_command + "\n"
                remove_libmemcached_result = run_command(remove_libmemcached_command, logfile, "Removal of libmemcached package")
                success = removed_libmemcached_result[0]
                logfile = removed_libmemcached_result[1]
                if not success:
                    return logfile
                
                libmemcached_installed = rpm_check("libmemcached-devel")
                if libmemcached_installed:
                    logfile.write("Failed to remove default version of libmemcached.\n")
                    print "Failed to remove default version of libmemcached.\n"
                    end_time = termination_string()
                    logfile.write(end_time)
                    return logfile
                else:
                    logfile.write("Successfully removed default version of libmemcached.\n")
                    print "Successfully removed default version of libmemcached."
                    time = current_time()
                    logfile.write("libmemcached removal finished at %s.\n" % time)
                    print "libmemcached removal finished at %s.\n" % time
                    
            # If libmemcached is not installed, there is no need to uninstall it, so the installation can continue.
            time = current_time()
            logfile.write("libmemcached-0.53 download/build/install started at %s.\n" % time)
            print "libmemcached-0.53 download/build/install started at %s.\n" % time
            logfile.write("libmemcached-0.53 will be downloaded, built, and installed.\n")
            print "libmemcached-0.53 will be downloaded, built, and installed."
            # Switch to downloads directory
            download_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep + "download")
            logfile.write("Switching to downloads directory: %s" % download_dir)
            print "Switching to downloads directory: %s" % download_dir
            os.chdir(download_dir)
            logfile.write("Operation succeeded.\n")
            print "Operation succeeded.\n"
            
            # wget libmemcached-0.53
            wget_command = "wget http://launchpad.net/libmemcached/1.0/0.53/+download/libmemcached-0.53.tar.gz --no-check-certificate"
            wget_command_result = run_command(wget_command, logfile, "Download of libmemcached-0.53.tar.gz")
            success = wget_command_result[0]
            logfile = wget_command_result[1]
            if not success:
                return logfile
            
            # Extract libmemcached-0.53
            logfile.write("Extracting libmemcached-0.53.\n")
            print "Extracting libmemcached-0.53.\n"
            tar_command = "tar xzvf libmemcached-0.53.tar.gz"
            tar_command_result = run_command(tar_command, logfile, "Extraction of libmemcached-0.53")
            success = tar_command_result[0]
            logfile = tar_command_result[1]
            if not success:
                return logfile
            
            # Take ownership of extracted directory
            extracted_dir = os.getcwd() + os.sep + "libmemcached-0.53"
            logfile.write("Changing ownership of %s to current user\n" % extracted_dir)
            print "Changing ownership of %s to current user\n" % extracted_dir
            uname = os.getuid()
            os.chown(extracted_dir, uname, -1)
            logfile.write("Operation succeeded.\n")
            print ("Operation succeeded.\n")
            
            # Change to extracted directory
            logfile.write("Switching to %s\n" % extracted_dir)
            print "Switching to %s\n" % extracted_dir
            os.chdir(extracted_dir)
            logfile.write("Working directory is now %s\n" % os.getcwd())
            print "Working directory is now %s\n" % os.getcwd()
            logfile.write("Operation succeeded\n.")
            print ("Operation succeeded\n.")
            
            # ./configure
            logfile.write("Running ./configure for libmemcached-0.53.\n")
            print "Running ./configure for  libmemcached-0.53.\n"
            lm_configure_command = "./configure"
            lm_configure_result = run_command(lm_configure_command, logfile, "Extraction of libmemcached-0.53")
            success = lm_configure_result[0]
            logfile = lm_configure_result[1]
            if not success:
                return logfile
            
            # make
            logfile.write("Running make for libmemcached-0.53.\n")
            print "Running make for  libmemcached-0.53.\n"
            lm_make_command = "make"
            lm_make_result = run_command(lm_make_command, logfile, "Extraction of libmemcached-0.53")
            success = lm_make_result[0]
            logfile = lm_make_result[1]
            if not success:
                return logfile
            
            # make install
            logfile.write("Running make install for libmemcached-0.53.\n")
            print "Running make install for  libmemcached-0.53.\n"
            lm_install_command = "make install"
            lm_install_result = run_command(lm_install_command, logfile, "Extraction of libmemcached-0.53")
            success = lm_install_result[0]
            logfile = lm_install_result[1]
            if not success:
                return logfile
            
            # Check libmemcached installation
            libmemcached053_installed = libmemcached053_check()
            if libmemcached053_installed:
                logfile.write("libmemcached-0.53 installed successfully.\n")
                print "libmemcached-0.53 installed successfully.\n"
                time = current_time()
                logfile.write("libmemcached-0.53 download/build/install finished at %s.\n" % time)
                print "libmemcached-0.53 download/build/install finished at %s.\n" % time
                # Flush the buffer and force a write to disk
                logfile.flush()
                os.fsync(logfile)
            else:
                error1 = "Error: Could not find libmemcached.so in /usr/local/lib.\n"
                error2 = "libmemcached-0.53 may not have installed properly.\n"
                logfile.write(error1)
                logfile.write(error2)
                print error1
                print error2
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        # End of libmemcached-0.53 installation code
        
        # Check for pgdg91 repo
        if postgresql91_repo:
            repo_string = "The repository at http://yum.postgresql.org/9.1/redhat/rhel-6-x86_64/pgdg-redhat91-9.1-5.noarch.rpm is already installed.\n"
            logfile.write(repo_string)
            print repo_string
        else:
            # Install Postgresql RPM
            time = current_time()
            logfile.write("pgdg91 repo installation started at %s.\n" % time)
            print "pgdg91 repo installation started at %s.\n" % time
            logfile.write("Adding the PostgreSQL 9.1 repo pgdg91...\n")
            print "Adding the PostgreSQL 9.1 repo pgdg91...\n"
            pg_repo_command = "rpm -i http://yum.postgresql.org/9.1/redhat/rhel-6-x86_64/pgdg-redhat91-9.1-5.noarch.rpm"
            logfile.write(pg_repo_command + "\n")
            print pg_repo_command + "\n"
            repo_tuple = commands.getstatusoutput(pg_repo_command)
            status = repo_tuple[0]
            output = repo_tuple[1]
            # Print output line by line
            output2 = output.split("\n")
            for line in output2:
                logfile.write(line + "\n")
                print line + "\n"
            if status == 0:
                rpm_installed = postgresql91_repocheck()
                if rpm_installed:
                    logfile.write("pgdg91 repo installed successfully.\n")
                    print "pgdg91 repo installed successfully.\n"
                    time = current_time()
                    logfile.write("pgdg91 repo installation finished at %s.\n" % time)
                    print "pgdg91 repo installation finished at %s.\n" % time
                    # Flush the buffer and force a write to disk after each successful installation
                    logfile.flush()
                    os.fsync(logfile)
                else:
                    logfile.write("PostgreSQL 9.1 repo failed to install.\n")
                    print "PostgreSQL 9.1 repo failed to install.\n"
                    end_time = termination_string()
                    logfile.write(end_time)
                    print end_time
                    return logfile
            elif status == 1:
                logfile.write("PostgreSQL 9.1 repo failed to install.\n")
                print "PostgreSQL 9.1 repo failed to install.\n"
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        
        # postgresql91-server
        if postgresql91_server_installed:
            logfile.write("postgresql91-server is already installed.\n")
            print "postgresql91-server is already installed.\n"
        else:
            time = current_time()
            logfile.write("postgresql91-server installation started at %s.\n" % time)
            print "postgresql91-server installation started at %s.\n" % time
            postgres91_result = yum_install("postgresql91-server", logfile)
            success = postgres91_result[0]
            logfile = postgres91_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("postgresql91-server installation finished at %s.\n" % time)
                print "postgresql91-server installation finished at %s.\n" % time
        
        # postgresql-91-contrib
        if postgresql91_contrib_installed:
            logfile.write("postgresql91-contrib is already installed.\n")
            print "postgresql91-contrib is already installed.\n"   
        else:
            time = current_time()
            logfile.write("postgresql91-contrib installation started at %s.\n" % time)
            print "postgresql91-contrib installation started at %s.\n" % time
            postgres91_contrib_result = yum_install("postgresql91-contrib", logfile)
            success = postgres91_contrib_result[0]
            logfile = postgres91_contrib_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("postgresql91-contrib installation finished at %s.\n" % time)
                print "postgresql91-contrib installation finished at %s.\n" % time
        
        # postgresql91-devel
        if postgresql91devel_installed:
            logfile.write("postgresql91-devel is already installed.\n")
            print "postgresql91-devel is already installed.\n"   
        else:
            time = current_time()
            logfile.write("postgresql91-devel installation started at %s.\n" % time)
            print "postgresql91-devel installation started at %s.\n" % time
            postgres91_devel_result = yum_install("postgresql91-devel", logfile)
            success = postgres91_devel_result[0]
            logfile = postgres91_devel_result[1]
            if not success:
                return logfile
            else:
                time = current_time()
                logfile.write("postgresql91-devel installation finished at %s.\n" % time)
                print "postgresql91-devel installation finished at %s.\n" % time
            
        logfile.write("RHEL x64 installation script completed successfully.\n")
        print "RHEL x64 installation script completed successfully.\n"
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile