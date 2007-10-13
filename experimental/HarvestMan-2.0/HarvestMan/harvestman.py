#! /usr/bin/env python
# -- coding: latin-1
""" HarvestMan - Extensible, modular and multithreaded Internet
    spider program using urllib2 and other python modules. This is
    the main module of HarvestMan.
    
    Version      - 2.0 beta 1.

    Author: Anand B Pillai <anand at harvestmanontheweb.com>

    HARVESTMAN is free software. See the file LICENSE.txt for information
    on the terms and conditions of usage, and a DISCLAIMER of ALL WARRANTIES.

 Modification History

    Created: Aug 2003

     Jan 23 2007          Anand      Changes to copy config file to ~/.harvestman/conf
                                     folder on POSIX systems. This file is also looked for
                                     if config.xml not found in curdir.
     Jan 25 2007          Anand      Simulation feature added. Also modified config.py
                                     to allow reading cmd line arguments when passing
                                     a config file using -C option.
     Feb 7 2007          Anand       Finished implementation of plugin feature. Crawl
                                     simulator is now a plugin.
     Feb 8 2007          Anand       Added swish-e integration as a plugin.
     Feb 11 2007         Anand       Changes in the swish-e plugin implementation,
                                     by using callbacks.
     Mar 2 2007          Anand       Renamed finish to finish_project. Moved
                                     Finish method from common.py to here and
                                     renamed it as finish(...). finish is never
                                     called at project end, but by default at
                                     program end.
     Mar 7 2007          Anand       Disabled urlserver option.
     Mar 15 2007         Anand       Added bandwidth calculation for determining
                                     max filesize before crawl. Need to add
                                     code to redetermine bandwidth when network
                                     interface changes.
     Apr 18 2007         Anand       Added the urltypes module for URL type
                                     definitions and replaced entries with it.
                                     Upped version number to 2.0 since this is
                                     almost a new program now!
     Apr 19 2007         Anand       Disabled urlserver option completely. Removed
                                     all referring code from this module, crawler
                                     and urlqueue modules. Moved code for grabbing
                                     URL to new hget module.
    Apr 24 2007          Anand       Made to work on Windows (XP SP2 Professional,
                                     Python 2.5)
    Apr 24 2007          Anand       Made the config directory creation/session
                                     saver features to work on Windows also.
    Apr 24 2007          Anand       Modified connector algorithm to flush data to
                                     temp files for hget. This makes sure that hget
                                     can download huge files as multipart.
    May 7 2007           Anand       Added plugin as option in configuration file.
                                     Added ability to process more than one plugin
                                     at once. Modified loading logic of plugins.
    May 10 2007          Anand       Replaced a number of private attributes in classes
                                     (with double underscores), to semi-private (one
                                     underscore). This helps in inheriting from these
                                     classes.

   Copyright (C) 2004 Anand B Pillai.     
"""     

__version__ = '2.0 b1'
__author__ = 'Anand B Pillai'

import config
import logger
from common.common import *
from harvestmanklass import HarvestMan

def process_plugins(plugins):
    """ Load all plugin modules """

    plugin_dir = os.path.abspath(os.path.join(os.path.dirname('__file__'), 'plugins'))

    if os.path.isdir(plugin_dir):
        sys.path.append(plugin_dir)
        # Load plugins specified in plugins list
        for plugin in plugins:
            # Load plugins
            try:
                logconsole('Loading plugin %s...' % plugin)
                M = __import__(plugin)
                func = getattr(M, 'apply_plugin', None)
                if not func:
                    logconsole('Invalid plugin %s, should define function "apply_plugin"!' % plugin)
                try:
                    logconsole('Applying plugin %s...' % plugin)
                    func()
                except Exception, e:
                    logconsole('Error while trying to apply plugin %s' % plugin)
                    logconsole('Error is:',str(e))
                    sys.exit(0)
            except ImportError, e:
                logconsole('Error importing plugin module %s' % plugin)
                logconsole('Error is:',str(e))
                logconsole('Invalid plugin: %s !' % plugin)
                sys.exit(0)

def prepare():
    """ Prepare """

    # Init Config Object
    InitConfig(config.HarvestManStateObject)
    # Initialize logger object
    InitLogger(logger.HarvestManLogger)

    cfg = GetObject('config')
    # Get program options
    if not cfg.resuming:
        cfg.get_program_options()

    process_plugins(cfg.plugins)

if __name__=="__main__":
    prepare()
    spider = HarvestMan()
    spider.main()
    

               
        

