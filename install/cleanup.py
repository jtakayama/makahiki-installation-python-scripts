import os
import datetime
import sys
import stat
from shutil import rmtree

def termination_string():
    """
    Gets the current system time and appends it to a termination notice.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    end_time = "Script exiting at %s\n" % time
    return end_time

def path_to_subdirectory(subdirectory):
    """
    Builds an absolute path to a subdirectory of the directory that this 
    file exists in.
    Parameters:
        1. subdirectory: Name of directory in the same directory as this file. 
    """
    runpath = os.path.dirname(os.path.realpath(__file__))
    pathdirs = runpath.split(os.sep)
    assembled_path = ""
    i = 0
    while i < len(pathdirs):
        if i == 0:
            assembled_path = pathdirs[i]
        else:
            assembled_path = assembled_path + os.sep + pathdirs[i]
        i = i + 1
    downloads_dir = assembled_path + os.sep + subdirectory
    return downloads_dir

def build_item_list(path_to_directory, exclude_list):
    """
    Lists all items in a directory, except for items in exclude_list.
    Parameters:
        1. path_to_directory: The directory being listed.
        2. exclude_list: Directories, files, etc. that are expected to be 
           in the directory and need to be excluded from the listing.
    """
    item_list = []
    all_files = os.listdir(path_to_directory)
    # Build list of files. Exclude project file download_readme.txt
    for entry in all_files:
        if entry not in exclude_list:
            item_list.append(path_to_directory + os.sep + entry)
    return item_list

def run(logfile):
    """
    Erases all files and directories in makahiki/install/download 
    except for download_readme.txt.
    Parameters:
        1. logfile: A file to log output to.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    start_time = "Makahiki downloads cleanup script started at %s\n" % time
    logfile.write(start_time)
    print start_time
    try:
        downloads_dir = path_to_subdirectory("download")
        delete_list = build_item_list(downloads_dir,["download_readme.txt"])
        if len(delete_list) == 0:
            logfile.write("Nothing to remove.\n")
            print "Nothing to remove."
        else:
            logfile.write("Cleaning up...\n")
            print "Cleaning up..."
            for entry in delete_list:
                mode = os.stat(entry).st_mode
                if stat.S_ISREG(mode):
                    logfile.write("Removing file: %s.\n" % entry)
                    print "Removing file: %s." % entry
                    os.remove(entry)
                elif stat.S_ISDIR(mode):
                    logfile.write("Removing directory recursively: %s.\n" % entry)
                    print "Removing directory recursively: %s." % entry
                    rmtree(entry)
            logfile.write("Done.\n")
            print "Done."
        closing = "\nMakahiki downloads cleanup script has completed.\n"
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile
    # Many of the os.* commands raise OSErrors.
    except OSError as ose:
        logfile.write("OSError: ")
        print "OSError: "
        oserror_output = " errno: %s\n filename: %s\n strerror: %s\n" % (ose.errno, ose.filename, ose.strerror) 
        logfile.write(oserror_output)
        print oserror_output
        logfile.write("Warning: Makahiki downloads cleanup did not complete successfully.\n")
        print "Warning: Makahiki downloads cleanup did not complete successfully.\n"
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile
        