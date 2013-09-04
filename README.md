Explanation
===========

The ./install/ directory contains installation scripts that install 
software packages for the Makahiki web server application. 

They are redundant now that Vagrant is being used to deploy 
development machines, but are retained here in case they 
happen to be useful later.

These scripts were originally located at the top level of the 
Makahiki project.

As of September 3, 2013, these scripts have been removed from the 
project and are not being actively developed. Use them at your own 
risk.

Documentation and Other Notes
=============================

Instructions to run the scripts are provided in ``./install/doc``.

To be able to run the scripts, clone the Makahiki repository 
(http://github.com/csdl/makahiki) and copy the ``install`` 
directory into the top-level ``makahiki`` directory.

The ubuntu_installer.py file and its subscripts were tested on 
Ubuntu 12.04.2 LTS x86 and x64 architectures.

The python273_sclinstall.py file was tested on CentOS 6.4 i386 
(x86 architecture) and CentOS 6.4 x86_64 (x64 architecture). It was 
intended for use on RHEL and CentOS 6, where it executes an SCL installation 
of Python 2.7.3.

The redhat_installer.py file and its subscripts were tested on 
CentOS 6.4 i386 and CentOS 6.4 x86_64. They were intended for use on RHEL 
and CentOS 6.

Both ubuntu_installer.py and redhat_installer.py depend on 
run_initialize_instance.py and run_update_instance.py. 

* run_initialize_instance.py ran the script ``makahiki/makahiki/scripts/initialize_instance.py --type-default``
* run_update_instance.py ran the script ``makahiki/makahiki/scripts/update_instance.py``

If the locations or operation of the makahiki/makahiki/scripts/initialize_instance.py script 
or makahiki/makahiki/scripts/update_instance.py scripts have changed, these scripts will 
no longer work.


