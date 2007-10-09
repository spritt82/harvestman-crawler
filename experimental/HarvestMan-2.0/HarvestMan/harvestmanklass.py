# -- coding: latin-1
""" harvestmanklass - Module containing HarvestMan crawler class.

    Author: Anand B Pillai <anand at harvestmanontheweb.com>

    Created: May 17 2007 Anand 
    
    May 17 2007          Anand       By renaming harvestman module to harvestmanklass
                                     and moving out plugin processing and start up
                                     logic to new harvestman module.

   Copyright (C) 2004 Anand B Pillai.     
"""     
import os, sys
from sgmllib import SGMLParseError
from shutil import copy
import cPickle, pickle

import urlqueue
import connector
import rules
import datamgr
import utils
import time
import threading
import shutil
import glob
import re

import urlparser

from common.common import *
from common.methodwrapper import MethodWrapperMetaClass

# Defining callback points
__callbacks__ = { 'run_saved_state_callback':'HarvestMan:run_saved_state',
                  'restore_state_callback':'HarvestMan:restore_state',
                  'run_projects_callback':'HarvestMan:run_projects',
                  'start_project_callback':'HarvestMan:start_project',
                  'finish_project_callback':'HarvestMan:finish_project',
                  'finalize_callback':'HarvestMan:finalize',                  
                  'init_callback' : 'HarvestMan:init'}

# Defining pluggable functions
__plugins__ = { 'clean_up_plugin':'HarvestMan:clean_up',
                'save_current_state_plugin': 'HarvestMan:save_current_state',
                'restore_state_plugin': 'HarvestMan:restore_state',
                'reset_state_plugin': 'HarvestMan:reset_state' }


class HarvestMan(object):
    """ Top level application class """

    # For supporting callbacks
    __metaclass__ = MethodWrapperMetaClass
    USER_AGENT = "HarvestMan 2.0"
        
    def __init__(self):
        """ Constructor """

        # project start page (on disk)
        self._projectstartpage = 'file://'
        # error file descriptor
        
    def finish_project(self):
        """ Actions to take after download is over for the current project """
        
        # Localise file links
        # This code sits in the data manager class
        dmgr = GetObject('datamanager')
        dmgr.post_download_setup()

        if not self._cfg.testing:
            if self._cfg.browsepage:
                browser = utils.HarvestManBrowser()
                browser.make_project_browse_page()

    def finalize(self):
        """ This function can be called at program exit or
        when handling signals to clean up """

        global RegisterObj
        
        # If this was started from a runfile,
        # remove it.
        if self._cfg.runfile:
            try:
                os.remove(self._cfg.runfile)
            except OSError, e:
                moreinfo('Error removing runfile %s.' % self._cfg.runfile)

        # inform user of config file errors
        if RegisterObj.userdebug:
            logconsole("Some errors were found in your configuration, please correct them!")
            for x in range(len(RegisterObj.userdebug)):
                logconsole(str(x+1),':', RegisterObj.userdebug[x])

        RegisterObj.userdebug = []
        logconsole('HarvestMan session finished.')

        RegisterObj.ini = 0
        RegisterObj.logger.shutdown()

        # Clean up lists inside data manager
        # GetObject('datamanager').clean_up()
        # Clean up lists inside rules module
        # GetObject('ruleschecker').clean_up()

    def save_current_state(self):
        """ Save state of objects to disk so program
        can be restarted from saved state """

        # If savesession is disabled, return
        if not self._cfg.savesessions:
            extrainfo('Session save feature is disabled.')
            return
        
        # Top-level state dictionary
        state = {}
        # All state objects are dictionaries

        # Get state of queue & tracker threads
        state['trackerqueue'] = GetObject('trackerqueue').get_state()
        # Get state of datamgr
        state['datamanager'] = GetObject('datamanager').get_state()
        # Get state of urlthreads 
        p = GetObject('datamanager')._urlThreadPool
        if p: state['threadpool'] = p.get_state()
        state['ruleschecker'] = GetObject('ruleschecker').get_state()

        # Get config object
        state['configobj'] = GetObject('config').copy()
        
        # Dump with time-stamp 
        fname = os.path.join(self._cfg.usersessiondir, '.harvestman_saves#' + str(int(time.time())))
        moreinfo('Saving run-state to file %s...' % fname)

        try:
            cPickle.dump(state, open(fname, 'wb'), pickle.HIGHEST_PROTOCOL)
            moreinfo('Saved run-state to file %s.' % fname)
        except (pickle.PicklingError, RuntimeError), e:
            logconsole(e)
            moreinfo('Could not save run-state !')
        
    def welcome_message(self):
        """ Print a welcome message """
        
        logconsole('Starting %s...' % self._cfg.progname)
        logconsole('Copyright (C) 2004, Anand B Pillai')
        logconsole(' ')

    def register_common_objects(self):
        """ Register common objects required by all projects """

        # Set myself
        SetObject(self)

        # Set verbosity in logger object
        GetObject('logger').verbosity = self._cfg.verbosity
        
        # Data manager object
        dmgr = datamgr.HarvestManDataManager()
        SetObject(dmgr)
        
        # Rules checker object
        ruleschecker = rules.HarvestManRulesChecker()
        SetObject(ruleschecker)
        
        # Connector object
        conn = connector.HarvestManNetworkConnector()
        SetObject(conn)

        # Connector factory
        conn_factory = connector.HarvestManUrlConnectorFactory(self._cfg.connections)
        SetObject(conn_factory)

        tracker_queue = urlqueue.HarvestManCrawlerQueue()
        SetObject(tracker_queue)

    def start_project(self):
        """ Start the current project """

        # crawls through a site using http/ftp/https protocols
        if self._cfg.project:
            info('*** Log Started ***\n')
            if not self._cfg.resuming:
                info('Starting project',self._cfg.project,'...')
            else:
                info('Re-starting project',self._cfg.project,'...')                
            
            # Write the project file 
            if not self._cfg.fromprojfile:
                projector = utils.HarvestManProjectManager()
                projector.write_project()

        # Make filters for rules object now only otherwise
        # it interferes with project-file writing
        GetObject('ruleschecker').make_filters()
        
        if not self._cfg.resuming:
            info('Starting download of url',self._cfg.url,'...')
        else:
            pass
            
        # Initialize datamgr
        dmgr = GetObject('datamanager')
        dmgr.initialize()
        
        # Read the project cache file, if any
        if self._cfg.pagecache:
            dmgr.read_project_cache()

        tracker_queue = GetObject('trackerqueue')

        if not self._cfg.resuming:
            # Configure tracker manager for this project
            if tracker_queue.configure():
                # start the project
                tracker_queue.crawl()
        else:
            tracker_queue.restart()

    def clean_up(self):
        """ Clean up actions to do, say after
        an interrupt """

        # Shut down logging on file
        moreinfo('Shutting down logging...')
        GetObject('logger').disableFileLogging()
        
        if self._cfg.fastmode:
            tq = GetObject('trackerqueue')
            tq.terminate_threads()

    def calculate_bandwidth(self):
        """ Calculate bandwidth. This also sets limit on
        maximum file size """

        # Calculate bandwidth
        bw = 0
        # Look for harvestman.conf in user conf dir
        conf = os.path.join(self._cfg.userconfdir, 'harvestman.conf')
        if not os.path.isfile(conf):
            conn = connector.HarvestManUrlConnector()
            urlobj = urlparser.HarvestManUrlParser('http://harvestmanontheweb.com/schemas/HarvestMan.xsd')
            bw = conn.calc_bandwidth(urlobj)
            bwstr='bandwidth=%f\n' % bw
            if bw:
                try:
                    open(conf,'w').write(bwstr)
                except IOError, e:
                    pass
        else:
            r = re.compile(r'(bandwidth=)(.*)')
            try:
                data = open(conf).read()
                m = r.findall(data)
                if m:
                    bw = float(m[0][-1])
            except IOError, e:
                pass

        return bw
        
    def create_initial_directories(self):
        """ Create initial directories """

        # Create user's HarvestMan directory on POSIX at $HOME/.harvestman and 
        # on Windows at $USERPROFILE/Local Settings/Application Data/HarvestMan
        harvestman_dir = ''
        
        if os.name == 'posix':
            homedir = os.environ.get('HOME')
            if homedir and os.path.isdir(homedir):
                harvestman_dir = os.path.join(homedir, '.harvestman')
                
        elif os.name == 'nt':
            profiledir = os.environ.get('USERPROFILE')
            if profiledir and os.path.isdir(profiledir):
                harvestman_dir = os.path.join(profiledir, 'Local Settings', 'Application Data','HarvestMan')

        if harvestman_dir:
            harvestman_conf_dir = os.path.join(harvestman_dir, 'conf')
            harvestman_sessions_dir = os.path.join(harvestman_dir, 'sessions')

            self._cfg.userdir = harvestman_dir
            self._cfg.userconfdir = harvestman_conf_dir
            self._cfg.usersessiondir = harvestman_sessions_dir

            if not os.path.isdir(harvestman_dir):
                try:
                    info('Looks like you are running HarvestMan for the first time in this machine')
                    info('Doing initial setup...')
                    info('Creating folder %s for storing HarvestMan application data...' % harvestman_dir)
                    os.makedirs(harvestman_dir)
                except (OSError, IOError), e:
                    logconsole(e)

            if not os.path.isdir(harvestman_conf_dir):
                try:
                    info('Creating "conf" sub-directory in %s...' % harvestman_dir)
                    os.makedirs(harvestman_conf_dir)

                    if os.path.isfile('config.xml'):
                        info('Copying current config file to %s...' % harvestman_conf_dir)
                        shutil.copy2('config.xml',harvestman_conf_dir)

                except (OSError, IOError), e:
                    logconsole(e)

            if not os.path.isdir(harvestman_sessions_dir):
                try:
                    info('Creating "sessions" sub-directory in %s...' % harvestman_dir)
                    os.makedirs(harvestman_sessions_dir)                        
                    info('Done.')
                except (OSError, IOError), e:
                    logconsole(e)
        
    def init(self):
        """ Initialization """

        SetUserAgent(self.USER_AGENT)

        self._cfg = GetObject('config')

        self.register_common_objects()
        self.create_initial_directories()

        # Calculate bandwidth and set max file size
        # bw = self.calculate_bandwidth()
        # Max file size is calculated as bw*timeout
        # where timeout => max time for a worker thread
        # if bw: self._cfg.maxfilesize = bw*self._cfg.timeout
                
    def setdefaultlocale(self):
        """ Set the default locale """

        # The default locale is set to
        # american encoding => en_US.ISO8859-1
        import locale
        
        if sys.platform != 'win32':
            locale.setlocale(locale.LC_ALL, locale.normalize(self._cfg.defaultlocale))
        else:
            # On windoze, the american locale does
            # not seem to be there.
            locale.setlocale(locale.LC_ALL, '')
        
    def set_locale(self):
        """ Set the locale (regional settings)
        for HarvestMan """

        # Import the locale module
        import locale
        
        # Get locale setting
        loc = self._cfg.locale

        # Try locale mappings
        trans_loc = locale.normalize(loc)
        # If we get a new locale which is
        # not american, then set it
        if trans_loc != loc and loc != 'american':
            try:
                extrainfo("Setting locale to",loc,"...")
                locale.setlocale(locale.LC_ALL,trans_loc)
                return True
            except locale.Error, e:
                # Set default locale upon any error
                self.setdefaultlocale()
                debug(str(e))
                
                return False
        else:
            # Set default locale if locale not found
            # in locale module
            self.setdefaultlocale()
            return False

    def run_projects(self):
        """ Run the HarvestMan projects specified in the config file """

        # Set locale - To fix errors with
        # regular expressions on non-english web
        # sites.
        self.set_locale()

        if self._cfg.verbosity:
            self.welcome_message()

        for x in range(len(self._cfg.urls)):
            # Get all project related vars
            url = self._cfg.urls[x]

            project = self._cfg.projects[x]
            verb = self._cfg.verbosities[x]
            tout = self._cfg.projtimeouts[x]
            basedir = self._cfg.basedirs[x]

            if not url or not project or not basedir:
                info('Invalid config options found!')
                if not url: info('Provide a valid url')
                if not project: info('Provide a valid project name')
                if not basedir: info('Provide a valid base directory')
                continue
            
            # Set the current project vars
            self._cfg.url = url
            self._cfg.project = project
            self._cfg.verbosity = verb
            self._cfg.projtimeout = tout
            self._cfg.basedir = basedir
                
            self.run_project()
            
    def run_project(self):
        """ Run a harvestman project """

        # Set project directory
        # Expand any shell variables used
        # in the base directory.
        self._cfg.basedir = os.path.expandvars(os.path.expanduser(self._cfg.basedir))
        
        if self._cfg.basedir:
            self._cfg.projdir = os.path.join( self._cfg.basedir, self._cfg.project )
            if self._cfg.projdir:
                if not os.path.exists( self._cfg.projdir ):
                    os.makedirs(self._cfg.projdir)

        # Set message log file
        # From 1.4 version message log file is created in the
        # project directory as <projectname>.log
        if self._cfg.projdir and self._cfg.project:
            self._cfg.logfile = os.path.join( self._cfg.projdir, "".join((self._cfg.project,
                                                                          '.log')))

        # Open stream to log file
        SetLogFile()
        
        try:
            if not self._cfg.testnocrawl:
                self.start_project()
        except (KeyboardInterrupt, ), e:
           if not self._cfg.ignoreinterrupts:
               self._cfg.keyboardinterrupt = True
               logconsole('Exception received=>',str(e))
               # dont allow to write cache, since it
               # screws up existing cache.
               GetObject('datamanager').conditional_cache_set()
               self.save_current_state()
                
               # sys.tracebacklimit = 0
               self.clean_up()

        self.finish_project()

    def reset_state(self):
        """ Reset state of certain objects/modules """

        # common
        ResetState()
        # Reset self._cfg
        self._cfg = GetObject('config')
        
    def restore_state(self, state_file):
        """ Restore state of some objects from a previous run """

        try:
            state = cPickle.load(open(state_file, 'rb'))
            # This has six keys - configobj, threadpool, ruleschecker,
            # datamanager, common and trackerqueue.

            # First update config object
            cfg = state.get('configobj')
            if cfg:
                for key,val in cfg.items():
                    self._cfg[key] = val
            else:
                print 'Config corrupted'
                # Corrupted object ?
                return -1

            # Open stream to log file
            SetLogFile()

            # Now update trackerqueue
            tq = GetObject('trackerqueue')
            ret = tq.set_state(state.get('trackerqueue'))
            if ret == -1:
                logconsole("Error restoring state in 'urlqueue' module - cannot proceed further!")
                return -1
            else:
                logconsole("Restored state in urlqueue module.")
            
            # Now update datamgr
            dm = GetObject('datamanager')
            ret = dm.set_state(state.get('datamanager'))
            if ret == -1:
                logconsole("Error restoring state in 'datamgr' module - cannot proceed further!")
                return -1
            else:
                dm.initialize()
                logconsole("Restored state in datamgr module.")                
            
            # Update threadpool if any
            pool = None
            if state.has_key('threadpool'):
                pool = dm._urlThreadPool
                ret = pool.set_state(state.get('threadpool'))
                logconsole('Restored state in urlthread module.')
            
            # Update ruleschecker
            rules = GetObject('ruleschecker')
            ret = rules.set_state(state.get('ruleschecker'))
            logconsole('Restored state in rules module.')
            
            return 0
        except (pickle.UnpicklingError, AttributeError, IndexError, EOFError), e:
            raise
            return -1

    def run_saved_state(self):

        # If savesession is disabled, return
        if not self._cfg.savesessions:
            extrainfo('Session save feature is disabled, ignoring save files')
            return -1
        
        # Set locale - To fix errors with
        # regular expressions on non-english web
        # sites.
        self.set_locale()
        
        # See if there is a file named .harvestman_saves#...
        sessions_dir = self._cfg.usersessiondir

        files = glob.glob(os.path.join(sessions_dir, '.harvestman_saves#*'))

        # Get the last dumped file
        if files:
            runfile = max(files)
            res = raw_input('Found HarvestMan save file %s. Do you want to re-run it ? [y/n]' % runfile)
            if res.lower()=='y':
                if self.restore_state(runfile)==0:
                    self._cfg.resuming = True
                    self._cfg.runfile = runfile

                    if self._cfg.verbosity:
                        self.welcome_message()
        
                    try:
                        if not self._cfg.testnocrawl:
                            self.start_project()
                    except (KeyboardInterrupt, EOFError, Exception):
                        if not self._cfg.ignoreinterrupts:
                            # dont allow to write cache, since it
                            # screws up existing cache.
                            GetObject('datamanager').conditional_cache_set()
                            # Disable tracebacks
                            sys.excepthook = None
                            self.save_current_state()
                            self.clean_up()

                    try:
                        self.finish_project()
                    except Exception, e:
                        # To catch errors at interpreter shutdown
                        pass
                else:
                    logconsole('Could not re-run saved state, defaulting to standard configuration...')
                    self._cfg.resuming = False
                    # Reset state
                    self.reset_state()
                    return -1
            else:
                logconsole('OK, falling back to default configuration...')
                return -1
        else:
            return -1
        pass

    def main(self):
        """ Main routine """

        self.init()
        
        # See if a crash file is there, then try to load it and run
        # program from crashed state.
        if self.run_saved_state() == -1:
            # No such crashed state or user refused to run
            # from crashed state. So do the usual run.
            self.run_projects()

        # Final cleanup
        self.finalize()
