redhat_readme.txt
=================

Contents:
-------------------------------------------------------------------------------
0.0. Introduction
1.0. Install Python 2.7.3 from SCL
2.0. Installing and Configuring Dependencies
2.1. Instructions
2.1.1. Check Prerequisites
2.1.2. Install System Environment Dependencies
2.1.3. Install Pip
2.1.4. Set Up the "makahiki" Virtual Environment
2.1.5. PostgreSQL Configuration
2.1.6. Install Dependencies With Pip
2.1.7. Environment Variables Configuration
2.1.8. Initialize Makahiki
2.1.9. Start the Server
2.1.9.1. Testing the Server Without a Web Browser
2.1.10. Update the Makahiki Instance
2.1.11. Check the Memcached Installation
2.1.11.1. Configuring Memcached for the First Time
2.1.11.2. Deactivating Memcached
2.1.11.3. Reactivating Memcached
Appendix A. Notes on Log Files
-------------------------------------------------------------------------------

0.0. Introduction
===============================================================================
This is a README file for the Makahiki installation scripts.

The redhat_installer.py script calls a set of Python scripts which partially 
automate the process of installing Makahiki on Red Hat Enterprise Linux 6 
and CentOS 6, x86 or x64.

In these instructions, a % represents your terminal prompt.

The scripts rely on the yum package manager. The scripts have been tested on 
CentOS 6 x86 and x64. Other Red Hat-based operating systems are not supported.

If you would prefer to install Makahiki manually, see 
https://makahiki.readthedocs.org/en/latest/installation-makahiki-unix.html.

Makahiki source code is available from https://github.com/csdl/makahiki.

WARNING:
-------------------------------------------------------------------------------
This script should not be used to deploy Makahiki on a cloud-based hosting 
system such as Heroku. For instructions to deploy Makahiki on Heroku, see
http://makahiki.readthedocs.org/en/latest/installation-makahiki-heroku.html.
-------------------------------------------------------------------------------

For Makahiki to work on RHEL 6, you must install Python 2.7.3.
The default version on RHEL 6 is Python 2.6.6, which cannot be changed without 
causing problems with operating system tools.
===============================================================================

1.0. Install Python 2.7.3 from SCL
===============================================================================
This step requires an Internet connection.

(1) Obtain the Makahiki source code:
This readme file usually comes with the Makahiki source code. If you already 
have the Makahiki source code, move or copy the top-level makahiki directory 
to your home directory:
-------------------------------------------------------------------------------
% cp makahiki ~/makahiki
-------------------------------------------------------------------------------
If you do not have the Makahiki source code, clone the GitHub repository into 
your user home directory. (You will need to install Git if you do not have 
it already.)
-------------------------------------------------------------------------------
% sudo yum install git
% cd ~/
% git clone http://github.com/csdl/makahiki.git
-------------------------------------------------------------------------------

(2) Switch to your top-level makahiki directory:
-------------------------------------------------------------------------------
% cd ~/makahiki
-------------------------------------------------------------------------------

(3) Run the install/python273_sclinstall.py script to install Python 2.7.3 
    from Red Hat Software Collections:
-------------------------------------------------------------------------------
% sudo ./install/python273_sclinstall.py
-------------------------------------------------------------------------------
This script will:
A. Install wget if it is not already installed.
B. Add the repository file for Red Hat's Python 2.7.3 software collection, 
   http://people.redhat.com/bkabrda/scl_python27.repo, to your 
   /etc/yum.repos.d directory.
C. Install Python 2.7.3 in /opt/rh/python27.

The script will create a log file in makahiki/install/logs with a filename of 
the format "install_sclinstall_<timestamp>.log," where <timestamp> is a 
sequence of numbers representing a timestamp in the system local time. For 
more information, see Appendix A.

After the script finishes, open a terminal and run this command 
to set Python 2.7.3 as the default in the current user's shell:
-------------------------------------------------------------------------------
% scl enable python27 bash
-------------------------------------------------------------------------------

IMPORTANT:
-------------------------------------------------------------------------------
You will need to run this command again each time you launch a new shell where 
you need Python 2.7.3.
-------------------------------------------------------------------------------

The rest of this guide assumes the use of the SCL installation 
of Python 2.7.3.

The SCL installation comes with easy_install (a.k.a. setuptools 
or distribute) and virtualenv (a.k.a. virtualenvwrapper).

Check that these packages are present:
-------------------------------------------------------------------------------
% which easy_install
/opt/rh/python27/root/usr/bin/easy_install
% which virtualenv
/opt/rh/python27/root/usr/bin/virtualenv
-------------------------------------------------------------------------------
===============================================================================

2.0. Installing and Configuring Dependencies
===============================================================================
The install/ directory in the top-level makahiki directory contains the 
redhat_installer.py script. It is used to install dependencies for Makahiki.

Usage of redhat_installer.py:
-------------------------------------------------------------------------------
./redhat_installer.py < --dependencies --arch < x86 | x64 > | --cleanup | 
                        --pip | --initialize_instance | --update_instance > 
    
All options require Python 2.7.3 or higher (but not Python 3) to run.
    
    --dependencies: Installs dependencies. This is the only option that 
      requires --arch to be specified. This script must be run with root 
      privileges.
    
    --cleanup: Deletes all files and directories in makahiki/install/download 
      except for download_readme.txt. Cleans up after dependency installation.

    --pip: Runs "pip install -r requirements.txt." The requirements.txt file 
      is located in the top-level makahiki directory.

    --initialize_instance: Initializes the Makahiki instance with default 
      settings, users, and data.

    --update_instance: Runs the makahiki/scripts/update_instance.py script 
      with default options.
    
    --arch: For RHEL 6, the x86 and x64 architectures are currently supported.
-------------------------------------------------------------------------------
===============================================================================

2.1. Instructions
===============================================================================
In these instructions, a % represents your terminal prompt.

It is assumed that your Makahiki installation is placed in the user's home 
directory. For a user named "robot," the user home directory would be 
/home/robot, and the makahiki directory would be at /home/robot/makahiki.
===============================================================================

2.1.1. Check Prerequisites
===============================================================================
(1.) Python 2.7.3 or higher (Not Python 3)
At a minimum, you need to have Python 2.7.3 or higher (but not Python 3) 
installed. If you have been following this guide, Python 2.7.3 is now 
the default Python for the current user's shell. Check this with 
python --version:
-------------------------------------------------------------------------------
% python --version
Python 2.7.3
-------------------------------------------------------------------------------

(2.) Internet connection
This software requires an internet connection in order to install packages.
===============================================================================

2.1.2. Install System Environment Dependencies
===============================================================================
Switch to your top-level makahiki directory:
-------------------------------------------------------------------------------
% cd ~/makahiki
-------------------------------------------------------------------------------

Run the script with your OS architecture specified:
-------------------------------------------------------------------------------
% sudo ./install/redhat_installer.py --dependencies --arch x86
-------------------------------------------------------------------------------
or
-------------------------------------------------------------------------------
% sudo ./install/redhat_installer.py --dependencies --arch x64
-------------------------------------------------------------------------------

The script installs these packages and their dependencies, if they are not 
already installed:
- All packages in the groupinstall of "Development tools"
- git
- gcc
- Python Imaging Library (packages: python-devel, python-imaging, libjpeg-devel, zlib-devel)
  - This also creates symbolic links for libjpeg.so and libz.so on x64 systems: 
    /usr/lib/libjpeg.so --> /usr/lib64/libjpeg.so
    /usr/lib/libz.so --> /usr/lib64/libz.so
- PostgreSQL 9.1:
  - http://yum.postgresql.org/9.1/redhat/rhel-6-x86_64/pgdg-redhat91-9.1-5.noarch.rpm
    will be added to the yum repositories. 
  - postgresql91-server 
  - postgresql91-contrib
  - postgresql91-devel
- memcached
- Uninstalls libmemcached-devel if installed
- libmemcached-0.53

The groupinstall may appear to freeze. This is normal: it installs a large 
number of packages, and the script does not print the output until it is 
finished. This step alone can take up to a half-hour on some connections.

The script will create a log file in makahiki/install/logs with a filename of 
the format "install_dependencies_<timestamp>.log," where <timestamp> is a 
sequence of numbers representing a timestamp in the system local time. 
For more information, see Appendix A.

OPTIONAL: 
-------------------------------------------------------------------------------
You can run the script with --cleanup to remove source files that were 
downloaded when building and installing libmemcached-0.53:
-------------------------------------------------------------------------------
% sudo ./install/redhat_installer.py --cleanup
-------------------------------------------------------------------------------
The script will create a log file in makahiki/install/logs with a filename of 
the format "install_cleanup_<timestamp>.log," where <timestamp> is a sequence 
of numbers representing a timestamp in the system local time. For more 
information, see Appendix A.
-------------------------------------------------------------------------------
===============================================================================

2.1.3. Install Pip
===============================================================================
If you are not the root user, you will need to log on as the root user.

Sudo does not work: it will try to execute the command in Python 2.6.6.

(1) In the terminal, enable Python 2.7.3 for the shell if you have not already:
-------------------------------------------------------------------------------
% scl enable python27 bash
-------------------------------------------------------------------------------

(2) Install pip:
-------------------------------------------------------------------------------
% easy_install pip
-------------------------------------------------------------------------------

(3) Install virtualenvwrapper:
-------------------------------------------------------------------------------
% pip install virtualenvwrapper
-------------------------------------------------------------------------------
===============================================================================

2.1.4. Set Up the "makahiki" Virtual Environment
===============================================================================
Add these lines to ~/.bashrc:
-------------------------------------------------------------------------------
# Virtualenvwrapper settings for makahiki
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/makahiki
# SCL Python settings
if [ ! $PROFILE_ENV ]; 
    then
        source /opt/rh/python27/root/usr/bin/virtualenvwrapper.sh
fi
------------------------------------------------------------------------------

After you are done editing .bashrc, source it to apply the 
new settings to your shell:
-------------------------------------------------------------------------------
% source ~/.bashrc
-------------------------------------------------------------------------------

NOTE:
-------------------------------------------------------------------------------
Because virtualenvwrapper was not installed to the default Python installation, 
the user will see this error at logon:
-------------------------------------------------------------------------------
/usr/bin/python: No module named virtualenvwrapper
virtualenvwrapper.sh: There was a problem running the initialization hooks.

If Python could not import the module virtualenvwrapper.hook_loader, 
check that virtualenv has been installed for
VIRTUALENVWRAPPER_PYTHON=/usr/bin/python and that PATH is 
set properly.
-------------------------------------------------------------------------------
To fix this, enable Python 2.7.3 again:

% scl enable python27 bash

Without Python 2.7.3 enabled in the shell, the system will not find the 
virtualenvwrapper installation.
-------------------------------------------------------------------------------

Switch to the top-level makahiki directory:
-------------------------------------------------------------------------------
% cd ~/makahiki
-------------------------------------------------------------------------------

Then, create the makahiki virtual environment: 
-------------------------------------------------------------------------------
% mkvirtualenv makahiki
-------------------------------------------------------------------------------

Creating a virtual environment should switch you to the virtual environment.
The terminal prompt will be preceded by the name of the virtual environment.
On RHEL, this looks like:
-------------------------------------------------------------------------------
(makahiki)[robot@computer makahiki]$
-------------------------------------------------------------------------------

If creating the virtual environment did not switch you to the virtual 
environment, use "workon" to switch to it:
-------------------------------------------------------------------------------
[robot@makahiki makahiki]$ workon makahiki
(makahiki)[robot@computer makahiki]$ 
-------------------------------------------------------------------------------

Check that your Python version in the virtual environment is 2.7.3:
-------------------------------------------------------------------------------
% python --version
Python 2.7.3
-------------------------------------------------------------------------------

NOTE:
-------------------------------------------------------------------------------
If you plan to develop Python scripts in this virtual environment, note that 
any script that is run with sudo will use the default Python 2.6.6.
-------------------------------------------------------------------------------
===============================================================================

2.1.5. PostgreSQL Configuration
===============================================================================
You should still be in the makahiki virtual environment.

Now that Postgresql is installed, you must enable it as a service 
and configure its authentication settings.

Initialize the Postgresql database and turn the Postgresql service on:
-------------------------------------------------------------------------------
% sudo service postgresql-9.1 initdb
Initializing database:                                     [  OK  ]
% sudo chkconfig postgresql-9.1 on
-------------------------------------------------------------------------------

The pg_hba.conf file is located in /var/lib/pgsql/9.1/data/pg_hba.conf.
It is owned by user postgres and group postgres, and it must be opened 
with sudo:
-------------------------------------------------------------------------------
% sudo vi /var/lib/pgsql/9.1/data/pg_hba.conf
-------------------------------------------------------------------------------
The vi editor is installed by default, but any text editor can be used.

You should edit the pg_hba.conf file so that the settings for "local", 
IPV4 local connections, and IPv6 local connections match the examples below:

Example pg_hba.conf settings:
-------------------------------------------------------------------------------
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
-------------------------------------------------------------------------------

WARNING:
-------------------------------------------------------------------------------
The "trust" setting lets local processes like Makahiki or the postgres 
database user connect to the database server without authentication. This is 
useful for development and configuration, but may not be secure enough for 
production use.
-------------------------------------------------------------------------------

Restart the Postgresql server after editing the file:
-------------------------------------------------------------------------------
% sudo service postgresql-9.1 restart
Stopping postgresql-9.1 service:                           [  OK  ]
Starting postgresql-9.1 service:                           [  OK  ]
-------------------------------------------------------------------------------
===============================================================================

2.1.6. Install Dependencies With Pip
===============================================================================
You should still be in the makahiki virtual environment.

Switch to the makahiki directory:
-------------------------------------------------------------------------------
% cd ~/makahiki
-------------------------------------------------------------------------------

Use "export" to temporarily add the Postgresql binaries to the 
system PATH. This is temporary. If you exit the current shell, 
you will need to do this again.
-------------------------------------------------------------------------------
% export PATH=/usr/pgsql-9.1/bin:$PATH
-------------------------------------------------------------------------------

Check that pg_config and psql are on the PATH.
-------------------------------------------------------------------------------
% which pg_config
/usr/pgsql-9.1/bin/pg_config
% which psql
/usr/pgsql-9.1/bin/psql
-------------------------------------------------------------------------------
If the system cannot find pg_config and psql, pip will not be able to compile 
the psycopg2 module.

Run the script with --pip:
-------------------------------------------------------------------------------
% ./install/redhat_installer.py --pip
-------------------------------------------------------------------------------
The list of packages that this step will attempt to install with pip are 
listed in the makahiki/requirements.txt file.

The script will create a log file in makahiki/install/logs with a filename of 
the format "install_pip_<timestamp>.log," where <timestamp> is a sequence of 
numbers representing a timestamp in the system local time. For more 
information, see Appendix A.
===============================================================================

2.1.7. Environment Variables Configuration
===============================================================================
The environment variables MAKAHIKI_DATABASE_URL and MAKAHIKI_ADMIN_INFO need 
to be added to the shell environment. To make them permanently available 
whenever you "workon makahiki," add these variables to the 
$WORKON_HOME/makahiki/bin/postactivate file:
-------------------------------------------------------------------------------
# Syntax: postgres://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>
export MAKAHIKI_DATABASE_URL=postgres://makahiki:makahiki@localhost:5432/makahiki

# Syntax: <admin_name>:<admin_password>
export MAKAHIKI_ADMIN_INFO=admin:admin
-------------------------------------------------------------------------------
Production instances of Makahiki should change the <admin_password> to 
something other than "admin."

You will need to do "workon makahiki" after you have edited the postactivate 
file for the changes to take effect:
-------------------------------------------------------------------------------
% workon makahiki
-------------------------------------------------------------------------------
Check that the variables have been set:
-------------------------------------------------------------------------------
% echo $MAKAHIKI_DATABASE_URL
postgres://makahiki:makahiki@localhost:5432/makahiki
% echo MAKAHIKI_ADMIN_INFO
admin:admin
-------------------------------------------------------------------------------
===============================================================================

2.1.8. Initialize Makahiki
===============================================================================
You should still be in the makahiki virtual environment.

Switch to the makahiki directory:
-------------------------------------------------------------------------------
% cd ~/makahiki
-------------------------------------------------------------------------------

WARNING:
-------------------------------------------------------------------------------
Running the script with --initialize_instance will:
- Install and/or update all Python packages required by Makahiki.
- Reinitialize the database contents and perform any needed database 
  migrations.
- Initialize the system with data.
- Set up static files.

This script should be run only a single time in production scenarios, because 
any subsequent configuration modifications will be lost if redhat_installer.py 
is invoked with --initialize_instance again. Use the --update_instance option
(discussed in Section 2.1.9, below) to update source code without losing 
subsequent configuration actions.

The script initializes the Makahiki database and populates it with default 
information and users. It is equivalent to running the standalone 
makahiki/makahiki/scripts/initialize_instance.py script with 
"--type default" options.
-------------------------------------------------------------------------------

Run the script with --initialize_instance:
-------------------------------------------------------------------------------
% ./install/redhat_installer.py --initialize_instance
-------------------------------------------------------------------------------
The script will create a log file in makahiki/install/logs with a filename of 
the format "install_initialize_instance_<timestamp>.log," where <timestamp> is 
a sequence of numbers representing a timestamp in the system local time. 
For more information, see Appendix A.
===============================================================================

2.1.9. Start the Server
===============================================================================
You should still be in the makahiki virtual environment.

Switch to the makahiki directory:
-------------------------------------------------------------------------------
% cd ~/makahiki/makahiki
-------------------------------------------------------------------------------

You can now start the web server using manage.py or gunicorn. The manage.py 
web server is better for development, while gunicorn is better for production 
use.

To start the server with manage.py:
-------------------------------------------------------------------------------
% ./manage.py runserver
-------------------------------------------------------------------------------

To start the server with gunicorn:
-------------------------------------------------------------------------------
% ./manage.py run_gunicorn
-------------------------------------------------------------------------------

In a web browser, go to http://localhost:8000 to see the landing page.
If you cannot view the page in a web browser, continue to section 2.1.9.1.
===============================================================================

2.1.9.1. Testing the Server Without a Web Browser
===============================================================================
If you are using a headless machine (no GUI) and cannot view the page 
in a web browser from another computer, you will need to run the server in the 
background and test it with wget:
-------------------------------------------------------------------------------
% ./manage.py runserver &
Validating models...

Development server is running at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
^M                              # Note: Press "enter" here to get command prompt.
% cd ~/
% mkdir test
% cd test
% wget http://127.0.0.1:8000
--2013-08-09 11:19:25--  http://127.0.0.1:8000/
Connecting to 127.0.0.1:8000... connected.
HTTP request sent, awaiting response... 302 FOUND
Location: http://127.0.0.1:8000/landing/ [following]
[09/Aug/2013 11:19:26] "GET / HTTP/1.0" 302 0
--2013-08-09 11:19:26--  http://127.0.0.1:8000/landing/
Connecting to 127.0.0.1:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: unspecified [text/html]
[09/Aug/2013 11:19:26] "GET /landing/ HTTP/1.0" 200 6181
Saving to: “index.html"

    [ <=>                                   ] 6,181       --.-K/s   in 0s

2013-08-09 11:19:26 (192 MB/s) - “index.html" saved [6181]
-------------------------------------------------------------------------------
If your HTTP response is "200 OK," the server is running correctly. You can 
delete the "test" directory when you are done:
-------------------------------------------------------------------------------
% cd ~/
% rm -rf test
-------------------------------------------------------------------------------

Because this server was started in the background with &, you cannot stop it 
with Control-C. You will need to find the PIDs of its processes first:
-------------------------------------------------------------------------------
% ps ax | grep manage.py
21791 tty1     S     0:00 python ./manage.py runserver
21798 tty1     Sl    0:52 /root/.virtualenvs/makahiki/bin/python ./manage.py ru
nserver
21893 tty1     S+    0:00 grep manage.py
% kill -9 21791 21798
% 
[1]+  Killed                 ./manage.py runserver
-------------------------------------------------------------------------------
The PID of a given process will be different each time it runs.
"kill -9 <PID>" forces the OS to stop the process.
Kill both the "python ./manage.py runserver" and 
"/root/.virtualenvs/makahiki/bin/python ./manage.py runserver" processes.
===============================================================================

2.1.10. Update the Makahiki Instance
===============================================================================
Makahiki is designed to support post-installation updating of your configured 
system when bug fixes or system enhancements become available. Updating an 
installed Makahiki instance using the redhat_installer.py script requires the 
following steps:

(1.) Close the running server in the shell process that is running Makahiki:
-------------------------------------------------------------------------------
% (type control-c in the shell running the makahiki server process)
-------------------------------------------------------------------------------

(2.) In the current shell or a new shell, go to the makahiki directory and 
     set up the Makahiki virtual environment:
-------------------------------------------------------------------------------
% cd ~/makahiki
% workon makahiki
-------------------------------------------------------------------------------

(3.) Download the updated source code into the Makahiki installation:
-------------------------------------------------------------------------------
% git pull origin master
-------------------------------------------------------------------------------

(4.) Run the redhat_installer.py script with --update_instance:
-------------------------------------------------------------------------------
% python ./install/redhat_installer.py --update_instance
-------------------------------------------------------------------------------

The script will create a log file in makahiki/install/logs with a filename of 
the format "install_update_instance_<timestamp>.log," where <timestamp> is 
a sequence of numbers representing a timestamp in the system local time. 
For more information, see Appendix A.

(5.) Start the server with runserver or gunicorn:
To start the server with manage.py:
-------------------------------------------------------------------------------
% ./manage.py runserver
-------------------------------------------------------------------------------

To start the server with gunicorn:
-------------------------------------------------------------------------------
% ./manage.py run_gunicorn
-------------------------------------------------------------------------------
===============================================================================

2.1.11. Check the Memcached Installation
===============================================================================
The provisioning script installed Memcached and libmemcached-0.53 on the 
system. If you plan to configure Memcached, you will need to test the 
Memcached installation.

In the virtual machine, switch to the makahiki/makahiki directory and run some 
commands in the manage.py shell:
-------------------------------------------------------------------------------
% sudo service memcached start
Starting memcached:                                        [  OK  ]
% export LD_LIBRARY_PATH_OLD=$LD_LIBRARY_PATH
% export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
% export MAKAHIKI_USE_MEMCACHED=True
% cd ~/makahiki/makahiki
% ./manage.py shell
Python 2.7.3 (default, Apr 10 2013, 05:46:21)
[GCC 4.6.3] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from django.core.cache import cache
>>> cache
<django_pylibmc.memcached.PyLibMCCache object at 0x8c93c4c>
>>> cache.set('test','Hello World')
True
>>> cache.get('test')
'Hello World'
>>> exit()
% unset MAKAHIKI_USE_MEMCACHED
% export LD_LIBRARY_PATH=$LD_LIBRARY_PATH_OLD
% unset LD_LIBRARY_PATH_OLD
% sudo service memcached stop
Stopping memcached:                                        [  OK  ]
-------------------------------------------------------------------------------
If running "manage.py shell" causes the error:
-----------------------------------------------------------------------------------
django.core.cache.backends.base.InvalidCacheBackendError: Could not import pylibmc.
-----------------------------------------------------------------------------------
then the LD_LIBRARY_PATH may not be set correctly in postactivate. This error 
occurs when MAKAHIKI_USE_MEMCACHED=True but LD_LIBRARY_PATH does not include 
the location of pylibmc.

If any of the following errors occur, then Memcached is not working:
(1) cache prints a blank to the console, or cache is a DummyCache.
(2) cache.set returns False or returns nothing.
(3) cache.get returns False, returns nothing, or causes a segmentation fault.
If so, make sure environment variables are set and Memcached is running..
===============================================================================

2.1.11.1. Configuring Memcached for the First Time
===============================================================================
Memcached is a backend cache for the Makahiki web server. 
Configuring memcached is optional.

If the tests in 2.1.11 succeed, you can configure Makahiki to use memcached. 
Add these lines to the end of the $WORKON_HOME/makahiki/bin/postactivate file:
-------------------------------------------------------------------------------
export MAKAHIKI_USE_MEMCACHED=True
# Don't add libmemcached paths more than once
if [ ! $LIBMEMCACHED_PATHS_ADDED ];
    then
        export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
        export LIBMEMCACHED_PATHS_ADDED=True
fi
-------------------------------------------------------------------------------

Then, workon makahiki to apply the changes:
-------------------------------------------------------------------------------
% workon makahiki
-------------------------------------------------------------------------------

Then, use chkconfig to set the memcached service to run at startup, and 
restart the memcached service:
-------------------------------------------------------------------------------
% sudo chkconfig memcached on
% sudo service memcached restart
-------------------------------------------------------------------------------
The memcached service will now run automatically at startup.

To test this, restart the computer. After the restart, you should be able to 
test memcached without setting any environment variables:
-------------------------------------------------------------------------------
% scl enable python27 bash
% workon makahiki
% cd ~/makahiki/makahiki
% ./manage.py shell
Python 2.7.3 (default, Dec  3 2012, 07:01:20)
[GCC 4.4.6 20120305 (Red Hat 4.4.6-4)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from django.core.cache import cache
>>> cache
<django_pylibmc.memcached.PyLibMCCache object at 0x1a4fc50>
>>> cache.set('test','Hello World')
True
>>> cache.get('test')
'Hello World'
>>> exit()
-------------------------------------------------------------------------------
If this test works, then the memcached service is running and will be used 
by Makahiki.
===============================================================================

2.1.11.2. Deactivating Memcached
===============================================================================
To deactivate memcached, edit $WORKON_HOME/makahiki/bin/postactivate to 
set MAKAHIKI_USE_MEMCACHED to False and comment out LD_LIBRARY_PATH settings:
-------------------------------------------------------------------------------
export MAKAHIKI_USE_MEMCACHED=False
# Don't add libmemcached paths more than once
#if [ ! $LIBMEMCACHED_PATHS_ADDED ];
#    then
#        export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
#        export LIBMEMCACHED_PATHS_ADDED=True
#fi
-------------------------------------------------------------------------------

Then stop the memcached service, and stop it from running at startup:
-------------------------------------------------------------------------------
% sudo service memcached stop
% sudo chkconfig memcached off
-------------------------------------------------------------------------------
The memcached service will no longer be used by Makahiki, and will no longer 
run at startup.

To verify this, test memcached once again:
-------------------------------------------------------------------------------
% scl enable python27 bash
% workon makahiki
% cd ~/makahiki/makahiki
% ./manage.py shell
Python 2.7.3 (default, Dec  3 2012, 07:01:20)
[GCC 4.4.6 20120305 (Red Hat 4.4.6-4)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from django.core.cache import cache
>>> cache
<django.core.cache.backends.dummy.DummyCache object at 0x1b20c90>
>>> cache.set('test','Hello World') == None
True
>>> exit()
-------------------------------------------------------------------------------
Cache should be a DummyCache, and cache.set == None should return True.
===============================================================================

2.1.11.3. Reactivating Memcached
===============================================================================
This section assumes that "scl enable python27 bash" has been run.

1. Edit $WORKON_HOME/makahiki/bin/postactivate to set MAKAHIKI_USE_MEMCACHED 
   to True, and uncomment the LD_LIBRARY_PATH settings:
-------------------------------------------------------------------------------
export MAKAHIKI_USE_MEMCACHED=True
# Don't add libmemcached paths more than once
if [ ! $LIBMEMCACHED_PATHS_ADDED ];
    then
        export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
        export LIBMEMCACHED_PATHS_ADDED=True
fi
-------------------------------------------------------------------------------

2. workon makahiki to apply the changes:
-------------------------------------------------------------------------------
% workon makahiki
-------------------------------------------------------------------------------

3a. If you just want to re-enable memcached temporarily, start the service:
-------------------------------------------------------------------------------
% sudo service memcached start
Starting memcached:                                        [  OK  ]
-------------------------------------------------------------------------------

3b. If you want to permanently set memcached to run at startup, do this:
-------------------------------------------------------------------------------
% sudo chkconfig memcached on
-------------------------------------------------------------------------------
===============================================================================

Appendix A. Notes on Log Files
===============================================================================
Log files are created by python273_sclinstall.py and redhat_installer.py in 
makahiki/install/logs. The log file names follow this format: 
<script-type>_<timestamp>.log

The timestamp in log file names breaks down as follows:
    year (4 places)
    month (2 places)
    day (2 places)
    hour (2 places)
    minute (2 places)
    second (2 places)
    microsecond (6 places)

The example timestamp 20130101000000102542 breaks down as follows:
Year: 2013, month: 01, day: 01, hour: 00, minute: 00, seconds: 00, 
microseconds: 102542.
===============================================================================