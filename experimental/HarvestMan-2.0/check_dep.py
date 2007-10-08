#!/usr/bin/env python
# -- coding: latin-1

# Dependency checker version 1
# Author: Anand B Pillai
#
# This tool is used to check dependencies for Harvestman 
#

welcome_message =  """
x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x
* Welcome to %s dependency checker*
x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x\n"""

import sys

def check_pyversion():
    """check dependency with python version used 
    """
    err = 0
    py = sys.executable
    
    if sys.version_info < (2,2):
        err = 1
        print 'Dependency failed: You need %s with version 2.2 or higher to run %s.' % (py, app)
    elif sys.version_info[:2] == (2,2):
        err = 2
        print '%s with version 2.2 detected, the following features will be disabled:'
        print '\t1.Tar Archival feature'
    else:
        version = "%d.%d.%d"%sys.version_info[:3]
        print '%s with version %s detected' % (py, version)

    return err 

if __name__=="__main__":
    
    if len(sys.argv) > 1 :
        app = sys.argv[1]
    else:
        app = 'HarvestMan'

    print welcome_message %app

    err = check_pyversion() 

    errormap = { 1: "%s will not run",
                 2: "%s will run but with limited features",
                 0: "%s will run without problems"}

    print errormap[err]%app
