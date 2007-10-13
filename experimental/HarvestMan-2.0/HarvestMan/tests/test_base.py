# -- coding: latin-1
""" Base module for unit tests

Created: Anand B Pillai <abpillai@gmail.com> Apr 17 2007

Copyright (C) 2007, Anand B Pillai.
"""

import sys, os

def setUpPaths():
    """ Set up paths """

    f = globals()['__file__']
    parentdir = os.path.dirname(os.path.dirname(f))
    print parentdir
    # Add modules in prev directory
    sys.path.append(parentdir)

def setUp():
    """ Set up """

    setUpPaths()
    
    from common.common import *
    import config
    import logger
    
    InitConfig(config.HarvestManStateObject)
    InitLogger(logger.HarvestManLogger)
