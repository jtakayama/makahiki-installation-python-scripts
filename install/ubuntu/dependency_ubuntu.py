import subprocess
import re
import os
import shlex
import datetime

def dpkg_check(packagename):
    """
    Checks the installation status of packages that need to be checked via 
    dpkg -s <packagename>. Returns True if installed, False if not.
    """
    dpkg_success = "Status: install ok installed"
    compare_result = False
    try:
        output = subprocess.check_output(shlex.split("dpkg -s %s" % packagename), stderr=subprocess.STDOUT)
        lines = output.split("\n")
        if lines[1] == dpkg_success:
            compare_result = True
    except subprocess.CalledProcessError as cpe:
        escaped_packagename = re.escape(packagename)
        dpkg_fail = re.compile("(Package `)(%s)+(\' is not installed and no info is available.)" % escaped_packagename)
        lines = cpe.output.split("\n")
        line0_result = dpkg_fail.match(lines[0])
        if (line0_result):
            compare_result = False
    return compare_result

def pip_check():
    """
    Checks if pip is installed on the system. Returns True if it is, 
    and False if it is not.
    """
    compare_result = False
    try:
        output = subprocess.check_output(shlex.split("pip --version"), stderr=subprocess.STDOUT)
        lines = output.split("\n")
        version_string = re.compile("(pip )(\d)+.(\d)+.(\d)")
        line0_result = version_string.match(lines[0])
        if not line0_result:
            compare_result = False
        else:
            compare_result = True
    except OSError as ose:
        # Assume not installed
        compare_result = False
    return compare_result

def virtualenvwrapper_check():
    """
    Checks if virtualenvwrapper is installed in the system. Returns True if 
    virtualenvwrapper is installed, and False if it is not.
    """
    compare_result = False
    try:
        output = subprocess.check_output(shlex.split("virtualenv --version"), stderr=subprocess.STDOUT)
        lines = output.split("\n")
        version_string = re.compile("(\d)+.(\d)+.(\d)")
        line0_result = version_string.match(lines[0])
        if not line0_result:
            compare_result = False
        else:
            compare_result = True
    except OSError as ose:
        # Assume not installed
        compare_result = False
    return compare_result

def libmemcached053_check():
    """
    Checks for the existence of the libmemcached.so library in 
    /usr/local/lib, which is where this script installs 
    libmemcached-0.53 after building it.
    """
    result = False
    try:
        # The libmemcached-0.53 install is not a dpkg and must be checked another way
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

def apt_get_install(packagename, logfile):
    """
    Installs <packagename> with "apt-get install -y <packagename>" and then 
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
        output = subprocess.check_output(shlex.split("apt-get install -y %s" % packagename), stderr=subprocess.STDOUT)
        logfile.write(output + "\n")
        print output
        # Check if RPM was installed
        is_installed = dpkg_check(packagename)
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
        output = subprocess.check_output(shlex.split(command), stderr=subprocess.STDOUT)
        logfile.write(output + "\n")
        print output
        logfile.write("%s successful:\n%s\n" % (message, command))
        print "%s successful:\n%s\n" % (message, command)
        success = True
    except CalledProcessError as cpe:
        # Print and log the error message
        logfile.write("CalledProcessError: ")
        print "CalledProcessError: "
        logfile.write(cpe.output)
        print cpe.output
        closing = "\n %s failed:\n" % command
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
    system commands. Writes its output to a logfile and prints 
    it to the console. It is left to the calling function to close 
    the logfile, which is returned.
    
    The target OS is Ubuntu Linux. x86 and x64 Ubuntu are supported.
    
    Warning: This will install or update to the newest available 
    versions of all packages specified.
    """
    
    # Write start time to file
    firstline = "Makahiki installation script for Ubuntu %s" % arch
    logfile.write(firstline)
    print firstline
    
    time = current_time()
    start_time = "Script started at %s\n" % time
    logfile.write(start_time)
    print start_time
    
    # Confirm that the user wants to continue.
    dependencies_list = "This script will install these packages and their dependencies:\n\
         wget,\n\
         git,\n\
         gcc,\n\
         python-setuptools,\n\
         pip,\n\
         python-imaging,\n\
         python-dev,\n\
         libjpeg-dev,\n\
         postgresql-9.1,\n\
         libpq-dev,\n\
         memcached,\n\
         all packages in build-essential,\n\
         g++,\n\
         libcloog-ppl-dev,\n\
         libcloog-ppl0,\n\
         libmemcached-0.53,\n\
         virtualenvwrapper\n"
    logfile.write(dependencies_list)
    print dependencies_list
    logfile.write("This script will uninstall libmemcached-dev if installed.\n")
    print "This script will uninstall libmemcached-dev if installed.\n"
    logfile.write("This script will also append to the current user's .bashrc file.\n")
    print ("This script will also append to the current user's .bashrc file.\n")
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
        logfile.write("Starting dependency installation for Ubuntu %s.\nChecking for dependencies...\n" % arch)
        print "Starting dependency installation for Ubuntu %s.\nChecking for dependencies...\n" % arch
        
        # Boolean variables for each dependency
        wget_installed = dpkg_check("wget")
        git_installed = dpkg_check("git")
        gcc_installed = dpkg_check("gcc")
        python_setuptools_installed = dpkg_check("python-setuptools")
        pip_installed = pip_check()
        python_imaging_installed = dpkg_check("python-imaging")
        python_dev_installed = dpkg_check("python-dev")
        libjpeg_dev_installed = dpkg_check("libjpeg-dev")
        postgresql91_installed = dpkg_check("postgresql-9.1")
        libpq_dev_installed = dpkg_check("libpq-dev")
        memcached_installed = dpkg_check("memcached")
        libmemcached_installed = dpkg_check("libmemcached-dev")
        libmemcached053_installed = libmemcached053_check()
        build_essential_installed = dpkg_check("build-essential")
        gplusplus_installed = dpkg_check("g++")
        libcloog_ppl_dev_installed = dpkg_check("libcloog-ppl-dev")
        libcloog_ppl0_installed = dpkg_check("libcloog-ppl0")
        virtualenvwrapper_installed = virtualenvwrapper_check()
        
        # wget
        if wget_installed:
            logfile.write("wget is already installed.\n")
            print "wget is already installed.\n"
        else:
            time = current_time()
            logfile.write("wget installation started at %s.\n" % time)
            print "wget installation started at %s.\n" % time
            wget_result = apt_get_install("wget", logfile)
            success = wget_result[0]
            logfile = wget_result[1]
            time = current_time()
            logfile.write("wget installation finished at %s.\n" % time)
            print "wget installation finished at %s.\n" % time
            if not success:
                return logfile
        
        # git
        if git_installed:
            logfile.write("git is already installed.\n")
            print "git is already installed.\n"
        else:
            time = current_time()
            logfile.write("git installation started at %s.\n" % time)
            print "git installation started at %s.\n" % time
            git_result = apt_get_install("git", logfile)
            success = git_result[0]
            logfile = git_result[1]
            time = current_time()
            logfile.write("git installation finished at %s.\n" % time)
            print "git installation finished at %s.\n" % time
            if not success:
                return logfile
            
        # gcc
        if gcc_installed:
            logfile.write("gcc is already installed.\n")
            print "gcc is already installed.\n"
        else:
            time = current_time()
            logfile.write("gcc installation started at %s.\n" % time)
            print "gcc installation started at %s.\n" % time
            gcc_result = apt_get_install("gcc", logfile)
            success = gcc_result[0]
            logfile = gcc_result[1]
            time = current_time()
            logfile.write("gcc installation finished at %s.\n" % time)
            print "gcc installation finished at %s.\n" % time
            if not success:
                return logfile
            
        # python-setuptools
        if python_setuptools_installed:
            logfile.write("python-setuptools is already installed.\n")
            print "python-setuptools is already installed.\n"
        else:
            time = current_time()
            logfile.write("python-setuptools installation started at %s.\n" % time)
            print "python-setuptools installation started at %s.\n" % time
            python_setuptools_result = apt_get_install("python-setuptools", logfile)
            success = python_setuptools_result[0]
            logfile = python_setuptools_result[1]
            time = current_time()
            logfile.write("python-setuptools installation finished at %s.\n" % time)
            print "python-setuptools installation finished at %s.\n" % time
            if not success:
                return logfile
            
        # pip
        if pip_installed:
            logfile.write("pip is already installed.\n")
            print "pip is already installed.\n"
        else:
            time = current_time()
            logfile.write("pip installation started at %s.\n" % time)
            print "pip installation started at %s.\n" % time
            logfile.write("easy_install pip\n")
            print "easy_install pip\n"
            try:
                USER_HOME = subprocess.check_output(["echo $HOME"], stderr=subprocess.STDOUT, shell=True)
                # Remove newline from expected "/home/<username>\n"
                USER_HOME = USER_HOME[:-1]
                USER_PROJECT_HOME = USER_HOME + os.sep + "makahiki"
                # cd to makahiki directory so easy_install will find its setup script
                os.chdir(USER_PROJECT_HOME)
                pip_output = subprocess.check_output(["easy_install", "pip"], stderr=subprocess.STDOUT)
                logfile.write(pip_output)
                print pip_output
                pip_installed = pip_check()
                if pip_installed:
                    time = current_time()
                    logfile.write("pip was successfully installed at %s.\n" % time)
                    print "pip was successfully installed at %s.\n" % time
                    # Flush the buffer and force a write to disk after each successful installation
                    logfile.flush()
                    os.fsync(logfile)
                else:
                    logfile.write("Error: pip failed to install.\n")
                    print "Error: pip failed to install.\n"
                    end_time = termination_string()
                    logfile.write(end_time)
                    print end_time
                    return logfile
            except subprocess.CalledProcessError as cpe:
                logfile.write("CalledProcessError: ")
                print "CalledProcessError: "
                logfile.write(cpe.output)
                print cpe.output
                logfile.write("Error: pip failed to install.\n")
                print "Error: pip failed to install.\n"
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
            
        logfile.write("Beginning installation of Python Imaging Library components python-imaging, python-dev, and libjpeg-dev.\n")
        print "Beginning installation of Python Imaging Library components python-imaging, python-dev, and libjpeg-dev.\n"
        
        # python-imaging
        if python_imaging_installed:
            logfile.write("python-imaging is already installed.\n")
            print "python-imaging is already installed.\n"
        else:
            time = current_time()
            logfile.write("python-imaging installation started at %s.\n" % time)
            print "python-imaging installation started at %s.\n" % time
            python_imaging_result = apt_get_install("python-imaging", logfile)
            success = python_imaging_result[0]
            logfile = python_imaging_result[1]
            time = current_time()
            logfile.write("python-imaging installation finished at %s.\n" % time)
            print "python-imaging installation finished at %s.\n" % time
            if not success:
                return logfile
            
        # python-dev
        if python_dev_installed:
            logfile.write("python-dev is already installed.\n")
            print "python-dev is already installed.\n"
        else:
            time = current_time()
            logfile.write("python-dev installation started at %s.\n" % time)
            print "python-dev installation started at %s.\n" % time
            python_dev_result = apt_get_install("python-dev", logfile)
            success = python_dev_result[0]
            logfile = python_dev_result[1]
            time = current_time()
            logfile.write("python-dev installation finished at %s.\n" % time)
            print "python-dev installation finished at %s.\n" % time
            if not success:
                return logfile
            
        # libjpeg-dev
        if libjpeg_dev_installed:
            logfile.write("libjpeg-dev is already installed.\n")
            print "libjpeg-dev is already installed.\n"
        else:
            time = current_time()
            logfile.write("libjpeg-dev installation started at %s.\n" % time)
            print "libjpeg-dev installation started at %s.\n" % time
            libjpeg_dev_result = apt_get_install("libjpeg-dev", logfile)
            success = libjpeg_dev_result[0]
            logfile = libjpeg_dev_result[1]
            time = current_time()
            logfile.write("libjpeg-dev installation finished at %s.\n" % time)
            print "libjpeg-dev installation finished at %s.\n" % time
            if not success:
                return logfile
            
        # Check for shared libraries and configure symbolic links if needed
        time = current_time()
        logfile.write("Configuring Python Imaging Library shared libraries: started at %s.\n" % time)
        print "Configuring Python Imaging Library shared libraries: started at %s.\n" % time
        # libjpeg.so
        try:
            libjpeg_stat = os.stat("/usr/lib/libjpeg.so")
            if libjpeg_stat:
                output1 = "Found libjpeg.so at /usr/lib/libjpeg.so\n"
                logfile.write(output1)
                print output1
        except OSError as libjpeg_error:
            if arch == "x86":
                try:
                    libjpeg_stat2 = os.stat("/usr/lib/i386-linux-gnu/libjpeg.so")
                    if libjpeg_stat2:
                        output2 = "Found: libjpeg.so at /usr/lib/i386-linux-gnu/libjpeg.so\n"
                        output3 = "Symbolic link will be created: /usr/lib/libjpeg.so --> /usr/lib/i386-linux-gnu/libjpeg.so\n"
                        output4 = "ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib/libjpeg.so\n"
                        logfile.write(output2)
                        logfile.write(output3)
                        logfile.write(output4)
                        print output2
                        print output3
                        print output4
                        subprocess.check_output(["ln", "-s", "/usr/lib/i386-linux-gnu/libjpeg.so", "/usr/lib/libjpeg.so"], stderr=subprocess.STDOUT)
                    else:
                        raise OSError
                except OSError as libjpeg_i386_error:
                    output5 = "Error: Could not find libjpeg.so in /usr/lib or /usr/lib/i386-linux-gnu.\n"
                    output6 = "Python Imaging Library-related packages may not have installed properly.\n"
                    logfile.write(output5)
                    logfile.write(output6)
                    print output5
                    print output6
                    end_time = termination_string()
                    logfile.write(end_time)
                    print end_time
                    return logfile 
            elif arch == "x64":
                try:
                    libjpeg_stat2 = os.stat("/usr/lib/x86_64-linux-gnu/libjpeg.so")
                    if libjpeg_stat2:
                        output2 = "Found: libjpeg.so at /usr/lib/x86_64-linux-gnu/libjpeg.so\n"
                        output3 = "Symbolic link will be created: /usr/lib/libjpeg.so --> /usr/lib/x86_64-linux-gnu/libjpeg.so\n"
                        output4 = "ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/libjpeg.so\n"
                        logfile.write(output2)
                        logfile.write(output3)
                        logfile.write(output4)
                        print output2
                        print output3
                        print output4
                        subprocess.check_output(["ln", "-s", "/usr/lib/x86_64-linux-gnu/libjpeg.so", "/usr/lib/libjpeg.so"], stderr=subprocess.STDOUT)
                    else:
                        raise OSError
                except OSError as libjpeg_x86_64_error:
                    output5 = "Error: Could not find libjpeg.so in /usr/lib or /usr/lib/x86_64-linux-gnu.\n"
                    output6 = "Python Imaging Library-related packages may not have installed properly.\n"
                    logfile.write(output5)
                    logfile.write(output6)
                    print output5
                    print output6
                    end_time = termination_string()
                    logfile.write(end_time)
                    print end_time
                    return logfile
            else:
                invalid_arch = "Error: Unsupported architecture for Ubuntu: %s\n" % arch
                logfile.write(invalid_arch)
                print invalid_arch
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
            
        # libz.so         
        try:
            libz_stat = os.stat("/usr/lib/libz.so")
            if libz_stat:
                output1 = "Found libz.so at /usr/lib/libz.so\n"
                logfile.write(output1)
                print output1
        except OSError as libz_error:
            if arch == "x86":
                try:
                    libz_stat2 = os.stat("/usr/lib/i386-linux-gnu/libz.so")
                    if libz_stat2:
                        output2 = "Found: libz.so at /usr/lib/i386-linux-gnu/libz.so\n"
                        output3 = "Symbolic link will be created: /usr/lib/libz.so --> /usr/lib/i386-linux-gnu/libz.so\n"
                        output4 = "ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib/libz.so\n"
                        logfile.write(output2)
                        logfile.write(output3)
                        logfile.write(output4)
                        print output2
                        print output3
                        print output4
                        subprocess.check_output(["ln", "-s", "/usr/lib/i386-linux-gnu/libz.so", "/usr/lib/libz.so"], stderr=subprocess.STDOUT)
                    else:
                        raise OSError
                except OSError as libz_i386_error:
                    output5 = "Error: Could not find libz.so in /usr/lib or /usr/lib/i386-linux-gnu.\n"
                    output6 = "Python Imaging Library-related packages may not have installed properly.\n"
                    logfile.write(output5)
                    logfile.write(output6)
                    print output5
                    print output6
                    end_time = termination_string()
                    logfile.write(end_time)
                    print end_time
                    return logfile
            elif arch == "x64":
                try:
                    libz_stat2 = os.stat("/usr/lib/x86_64-linux-gnu/libz.so")
                    if libz_stat2:
                        output2 = "Found: libz.so at /usr/lib/x86_64-linux-gnu/libz.so\n"
                        output3 = "Symbolic link will be created: /usr/lib/libz.so --> /usr/lib/x86_64-linux-gnu/libz.so\n"
                        output4 = "ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/libz.so\n"
                        logfile.write(output2)
                        logfile.write(output3)
                        logfile.write(output4)
                        print output2
                        print output3
                        print output4
                        subprocess.check_output(["ln", "-s", "/usr/lib/x86_64-linux-gnu/libz.so", "/usr/lib/libz.so"], stderr=subprocess.STDOUT)
                    else:
                        raise OSError
                except OSError as libz_x86_64_error:
                    output5 = "Error: Could not find libz.so in /usr/lib or /usr/lib/x86_64-linux-gnu.\n"
                    output6 = "Python Imaging Library-related packages may not have installed properly.\n"
                    logfile.write(output5)
                    logfile.write(output6)
                    print output5
                    print output6
                    end_time = termination_string()
                    logfile.write(end_time)
                    print end_time
                    return logfile
            else:
                invalid_arch = "Error: Unsupported architecture for Ubuntu: %s\n" % arch
                logfile.write(invalid_arch)
                print invalid_arch
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        
        time = current_time()
        logfile.write("Configuring Python Imaging Library shared libraries: finished at %s.\n" % time)
        print "Configuring Python Imaging Library shared libraries: finished at %s.\n" % time
        logfile.write("Installation of Python Imaging Library components is complete.\n")
        print "Installation of Python Imaging Library components is complete.\n"
        
        # PostgreSQL 9.1
        if postgresql91_installed:
            logfile.write("postgresql-9.1 is already installed.\n")
            print "postgresql-9.1 is already installed.\n"
        else:
            time = current_time()
            logfile.write("postgresql-9.1 installation started at %s.\n" % time)
            print "postgresql-9.1 installation started at %s.\n" % time
            postgresql_91_result = apt_get_install("postgresql-9.1", logfile)
            success = postgresql_91_result[0]
            logfile = postgresql_91_result[1]
            time = current_time()
            logfile.write("postgresql-9.1 installation finished at %s.\n" % time)
            print "postgresql-9.1 installation finished at %s.\n" % time
            if not success:
                return logfile
        
        #libpq-dev
        if libpq_dev_installed:
            logfile.write("libpq-dev is already installed.\n")
            print "libpq-dev is already installed.\n"
        else:
            time = current_time()
            logfile.write("libpq-dev installation started at %s.\n" % time)
            print "libpq-dev installation started at %s.\n" % time
            libpq_dev_result = apt_get_install("libpq-dev", logfile)
            success = libpq_dev_result[0]
            logfile = libpq_dev_result[1]
            time = current_time()
            logfile.write("libpq-dev installation finished at %s.\n" % time)
            print "libpq-dev installation finished at %s.\n" % time
            if not success:
                return logfile
            
        #memcached
        if memcached_installed:
            logfile.write("memcached is already installed.\n")
            print "memcached is already installed.\n"
        else:
            time = current_time()
            logfile.write("memcached installation started at %s.\n" % time)
            print "memcached installation started at %s.\n" % time
            memcached_result = apt_get_install("memcached", logfile)
            success = memcached_result[0]
            logfile = memcached_result[1]
            time = current_time()
            logfile.write("memcached installation finished at %s.\n" % time)
            print "memcached installation finished at %s.\n" % time
            if not success:
                return logfile
        
        # Beginning of libmemcached-0.53 installation code
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
                logfile.write("libmemcached-dev removal started at %s.\n" % time)
                print "libmemcached-dev removal started at %s.\n" % time
                logfile.write("libmemcached-dev will be removed.\n")
                print "libmemcached-dev will be removed.\n"
                remove_libmemcached_command = "apt-get remove -y libmemcached-dev"
                logfile.write(remove_libmemcached_command + "\n")
                print remove_libmemcached_command + "\n"
                remove_libmemcached_result = run_command(remove_libmemcached_command, logfile, "Removal of libmemcached package")
                success = removed_libmemcached_result[0]
                logfile = removed_libmemcached_result[1]
                if not success:
                    return logfile
                
                libmemcached_installed = dpkg_check("libmemcached-dev")
                if libmemcached_installed:
                    logfile.write("Failed to remove default version of libmemcached-dev.\n")
                    print "Failed to remove default version of libmemcached-dev.\n"
                    end_time = termination_string()
                    logfile.write(end_time)
                    return logfile
                else:
                    logfile.write("Successfully removed default version of libmemcached-dev.\n")
                    print "Successfully removed default version of libmemcached-dev."
                    time = current_time()
                    logfile.write("libmemcached-dev removal finished at %s.\n" % time)
                    print "libmemcached-dev removal finished at %s.\n" % time
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
            
            # build-essential
            if build_essential_installed:
                logfile.write("build-essential is already installed.\n")
                print "build-essential is already installed.\n"
            else:
                time = current_time()
                logfile.write("build-essential installation started at %s.\n" % time)
                print "build-essential installation started at %s.\n" % time
                build_essential_result = apt_get_install("build-essential", logfile)
                success = build_essential_result[0]
                logfile = build_essential_result[1]
                time = current_time()
                logfile.write("build-essential installation finished at %s.\n" % time)
                print "build-essential installation finished at %s.\n" % time
                if not success:
                    return logfile
            
            # g++
            if gplusplus_installed:
                logfile.write("g++ is already installed.\n")
                print "g++ is already installed.\n"
            else:
                time = current_time()
                logfile.write("g++ installation started at %s.\n" % time)
                print "g++ installation started at %s.\n" % time
                gplusplus_result = apt_get_install("g++", logfile)
                success = gplusplus_result[0]
                logfile = gplusplus_result[1]
                time = current_time()
                logfile.write("g++ installation finished at %s.\n" % time)
                print "g++ installation finished at %s.\n" % time
                if not success:
                    return logfile
            
            # libcloog-ppl-dev
            if libcloog_ppl_dev_installed:
                logfile.write("libcloog-ppl-dev is already installed.\n")
                print "libcloog-ppl-dev is already installed.\n"
            else:
                time = current_time()
                logfile.write("libcloog-ppl-dev installation started at %s.\n" % time)
                print "libcloog-ppl-dev installation started at %s.\n" % time
                libcloog_ppl_dev_result = apt_get_install("libcloog-ppl-dev", logfile)
                success = libcloog_ppl_dev_result[0]
                logfile = libcloog_ppl_dev_result[1]
                time = current_time()
                logfile.write("libcloog-ppl-dev installation finished at %s.\n" % time)
                print "libcloog-ppl-dev installation finished at %s.\n" % time
                if not success:
                    return logfile
            
            # libcloog-ppl0
            if libcloog_ppl0_installed:
                logfile.write("libcloog-ppl0 is already installed.\n")
                print "libcloog-ppl0 is already installed.\n"
            else:
                time = current_time()
                logfile.write("libcloog-ppl0 installation started at %s.\n" % time)
                print "libcloog-ppl0 installation started at %s.\n" % time
                libcloog_ppl0_result = apt_get_install("libcloog-ppl0", logfile)
                success = libcloog_ppl0_result[0]
                logfile = libcloog_ppl0_result[1]
                time = current_time()
                logfile.write("libcloog-ppl0 installation finished at %s.\n" % time)
                print "libcloog-ppl0 installation finished at %s.\n" % time
                if not success:
                    return logfile
            
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
                # Flush the buffer and force a write to disk
                logfile.flush()
                os.fsync(logfile)
                time = current_time()
                logfile.write("libmemcached-0.53 download/build/install finished at %s.\n" % time)
                print "libmemcached-0.53 download/build/install finished at %s.\n" % time
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
        
        #virtualenvwrapper
        if virtualenvwrapper_installed:
            logfile.write("virtualenvwrapper is already installed.\n")
            print "virtualenvwrapper is already installed.\n"
        else:
            time = current_time()
            logfile.write("virtualenvwrapper installation started at %s.\n" % time)
            print "virtualenvwrapper installation started at %s.\n" % time
            logfile.write("pip install virtualenvwrapper\n")
            print "pip install virtualenvwrapper\n"
            virtualenvwrapper_output = subprocess.check_output(["pip", "install",  "virtualenvwrapper"], stderr=subprocess.STDOUT)
            logfile.write(virtualenvwrapper_output)
            print virtualenvwrapper_output
            virtualenvwrapper_installed = virtualenvwrapper_check()
            if virtualenvwrapper_installed:
                time = current_time()
                logfile.write("virtualenvwrapper was successfully installed at %s.\n" % time)
                print "virtualenvwrapper was successfully installed at %s.\n" % time
                # Flush the buffer and force a write to disk after each successful installation
                logfile.flush()
                os.fsync(logfile)
            else:
                logfile.write("Error: virtualenvwrapper failed to install.\n")
                print "Error: virtualenvwrapper failed to install.\n"
                end_time = termination_string()
                logfile.write(end_time)
                print end_time
                return logfile
        
        time = current_time()
        logfile.write("Appending virtualenvwrapper settings to user's ~./bashrc: started at %s." % time)
        print "Appending virtualenvwrapper settings to user's ~./bashrc: started at %s." % time
        # bashrc
        USER_HOME = subprocess.check_output(["echo $HOME"], stderr=subprocess.STDOUT, shell=True) 
        # Remove newline from expected "/home/<username>\n"
        USER_HOME = USER_HOME[:-1]
        MAKAHIKI_HOME = USER_HOME + os.sep + "makahiki"
        bashrc_output0 = "Appending these lines to user's ~./bashrc file:\n"
        bashrc_output1 = "# Virtualenvwrapper settings for makahiki\n"
        bashrc_output2 = "export WORKON_HOME=%s/.virtualenvs\n" % USER_HOME
        bashrc_output3 = "export PROJECT_HOME=%s\n" % MAKAHIKI_HOME
        bashrc_output4 = "source /usr/local/bin/virtualenvwrapper.sh\n"
        logfile.write(bashrc_output0 + bashrc_output1 + bashrc_output2 + bashrc_output3 + bashrc_output4)
        print bashrc_output0 + bashrc_output1 + bashrc_output2 + bashrc_output3 + bashrc_output4
        # Append to ~/.bashrc
        bashrc = open(USER_HOME + "/.bashrc", 'a')
        bashrc.write("\n# Virtualenvwrapper settings for makahiki\n")
        bashrc.write("export WORKON_HOME=%s/.virtualenvs\n" % USER_HOME)
        bashrc.write("export PROJECT_HOME=%s\n" % MAKAHIKI_HOME)
        bashrc.write("source /usr/local/bin/virtualenvwrapper.sh\n")
        bashrc.close()
        # Done appending to file
        time = current_time()
        logfile.write("Finished appending to ~/.bashrc file at %s.\n" % time)
        print "Finished appending to ~/.bashrc file at %s.\n" % time
        
        # Done with installation process   
        logfile.write("Script completed successfully.\n")
        print ("Script completed successfully.\n") 
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile
