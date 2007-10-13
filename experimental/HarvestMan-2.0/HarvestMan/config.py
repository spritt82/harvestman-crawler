# -- coding: latin-1
""" config.py - Module to keep configuration options
    for HarvestMan program and its related modules. This 
    module is part of the HarvestMan program.

    Author: Anand B Pillai <anand at harvestmanontheweb.com>

    For licensing information see the file LICENSE.txt that
    is included in this distribution.


    Jan 23 2007      Anand    Added code to check config in $HOME/.harvestman.
                              Added control-var for session saving feature.
    Feb 8 2007       Anand    Added config support for loading plugins. Added
                              code for swish-e plugin.

    Feb 11 2007      Anand    Re-wrote configuration parsing using generic option
                              parser.

    Mar 03 2007      Anand    Removed old option parsing dictionary and some
                              obsolete code. Added option for changing time gap
                              between downloads in config file. Removed command
                              line option for urllistfile/urltree file. Added
                              option to read multiple start URLs from a file.
                              Modified behaviour so that if a source of URL is
                              specified (command-line, URL file etc), any URLs
                              in config file is skipped. Set urlserver option
                              as default.
   Mar 06 2007       Anand    Reset default option to queue.
   April 11 2007     Anand    Renamed xmlparser module to configparser.
   April 20 2007     Anand    Added options for hget.
   eMay 7 2007       Anand    Modified option parsing for plugin option.
   
   Copyright (C) 2004 Anand B Pillai.                              

"""

__version__ = '2.0 b1'
__author__ = 'Anand B Pillai'

USAGE1 = """\
 %(program)s [options] [optional URL]
 
%(appname)s %(version)s %(maturity)s: An extensible, multithreaded web crawler.
Author: Anand B Pillai

Mail bug reports and suggestions to <abpillai at gmail dot com>."""

USAGE2 = """\
 %(program)s [options] URL(s) | file(s)
 
%(appname)s %(version)s %(maturity)s: A multithreaded web downloader based on HarvestMan.
Author: Anand B Pillai

The program accepts URL(s) or an input file(s) containing a number of URLs,
one per line. If a file is passed as input, any other program option
passed is applied for every URL downloaded using the file.

Mail bug reports and suggestions to <abpillai at gmail dot com>."""

import os, sys
import re
import configparser
import options
import urlparser

from common.optionparser import *
from common.progress import TextProgress

class HarvestManStateObject(dict):
    """ Internal config class for the program """

    def __init__(self):
        """ Initialize dictionary with the most common
        settings and their values """

        self._init1()
        self._init2()

    def _init1(self):

        self.items_to_skip=[]
        # Version for harvestman
        self.version='2.0'
        # Maturity for harvestman
        self.maturity="beta 1"
        # Single appname property for hget/harvestman
        self.appname='HarvestMan'
        self.progname="".join((self.appname," ",self.version," ",self.maturity))
        self.program = sys.argv[0]
        self.url=''
        self.urls = []
        self.project=''
        self.projects = []
        self.combine = False
        self.basedir=''
        self.basedirs = []
        self.verbosities=[]
        self.projtimeouts = []
        self.urlmap = {}
        self.archive = 0
        self.archformat = 'bzip'
        self.urlheaders = 1
        self.configfile = 'config.xml'
        self.projectfile = ''         
        self.proxy=''
        self.puser=''
        self.ppasswd=''
        self.proxyenc=True
        self.username=''   
        self.passwd=''     
        self.proxyport=0
        self.errorfile='errors.log'
        self.localise=2
        self.jitlocalise=0
        self.images=1
        self.depth=10
        self.html=1
        self.robots=1
        self.eserverlinks=0
        self.epagelinks=1
        self.fastmode=1
        self.usethreads=1
        self.maxfiles=5000
        self.maxextservers=0
        self.maxextdirs=0
        self.retryfailed=1
        self.extdepth=0
        self.maxtrackers=4
        self.urlfilter=''
        self.wordfilter=''
        self.inclfilter=[]
        self.exclfilter=[]
        self.allfilters=[]
        self.serverfilter=''
        self.serverinclfilter=[]
        self.serverexclfilter=[]
        self.allserverfilters=[]
        self.urlpriority = ''
        self.serverpriority = ''
        self.urlprioritydict = {}
        self.serverprioritydict = {}
        self.verbosity=2
        self.verbosity_default=2
        # timeout for worker threads is a rather
        # large 20 minutes.
        self.timeout=1200.00
        # timeout for sockets is a modest
        # two minutes
        self.socktimeout = 120.00
        # Time out for fetchers is a rather
        # small 4 minutes
        self.fetchertimeout = 240.0
        self.getimagelinks=1
        self.getstylesheets=1
        self.threadpoolsize=10
        self.renamefiles=0
        self.fetchlevel=0
        self.browsepage=0
        self.htmlparser=0
        self.checkfiles=1
        self.pagecache=1
        self.cachefound=0
        self._error=''
        self.starttime=0
        self.endtime=0
        self.javascript = True
        self.javaapplet = True
        self.connections=5
        self.cachefileformat='pickled' 
        self.testing = False 
        self.testnocrawl = False
        self.nocrawl = False
        self.ignoreinterrupts = False
        # Set to true when a kb interrupt is caught
        self.keyboardinterrupt = False
        # Differentiate between sub-domains of a domain ?
        # When set to True, subdomains act like different
        # domains, so they are filtered out for fetchlevel<=1
        self.subdomain = True
        self.getquerylinks = False 
        self.requests = 5
        self.bytes = 20.00 # Not used!
        self.projtimeout = 1800.00
        self.downloadtime = 0.0
        self.locale = 'C'
        self.defaultlocale = 'C'
        self.timelimit = -1
        self.terminate = False
        self.datacache = False
        self.urlserver = False
        self.urlhost = '127.0.0.1'
        self.urlport = 0
        self.urlserver_protocol='tcp'
        self.blocking = False
        self.junkfilter = True
        self.junkfilterdomains = True
        self.junkfilterpatterns = True
        self.urltreefile = ''
        self.urlfile = ''
        self.maxfilesize=5242880
        self.minfilesize=0
        self.format = 'xml'
        self.rawsave = False
        self.fromprojfile = False
        # For running from previous states.
        self.resuming = False
        self.runfile = None
        # Control var for session-saver feature.
        self.savesessions = True
        # List of enabled plugins
        self.plugins = []
        # Control var for simulation feature
        self.simulate = False
        # Time to sleep between requests
        self.sleeptime = 1.0
        self.randomsleep = True
        # Internal flag for asyncore
        self.useasyncore = True
        # For http compression
        self.httpcompress = True
        # Type of URLs which can be
        # set to skip any rules we define
        # This is not a user configurable
        # option, but can be configured in
        # plugins, of course.
        self.skipruletypes = []
        # Number of parts to split a file
        # to, for multipart http downloads
        self.numparts = 4
        # Flag to force multipart downloads off
        self.nomultipart = False
        # Flag to indicate that a multipart
        # download is in progress
        self.multipart = False
        # Links offset start - this will
        # skip the list of child links of a URL
        # to the given value
        self.linksoffsetstart = 0
        # Links offset value - this will skip
        # the list of child links of a URL
        # after the given value
        self.linksoffsetend = -1
        # Current progress object
        self.progressobj = TextProgress()
        # Flag for forcing multipart downloads
        self.forcesplit = False
        # Flag for flushing data for hget
        # If True, data is flushed at interval
        # to file objects to save memory. If False, then
        # data is kept in memory and not flushed.
        # Default is False.
        self.flushdata = False
        # Flag for inmem - opposite of flushdata
        # used only by hget
        self.inmem = False
        # Hget outfile - default empty string
        self.hgetoutfile = ''
        # Hget output directory - default current directory
        self.hgetoutdir = '.'
        # Hget verbosity flag - default False
        self.hgetverbose = False
        # Hget temp flag - default False
        self.hgetnotemp = False
        # Hget mirror file
        self.mirrorfile = ''
        # Hget resume mode
        self.canresume = True
        
    def copy(self):
        # Set non-picklable objects to None type
        self.progressobj = None
        return super(HarvestManStateObject, self).copy()

    def get_project_object(self):
        """ Return an object suitable to write as a project
        file """

        self.progressobj = None
        return self
    
    def _init2(self):
        
        # For mapping xml entities to config entities
        
        self.xml_map = { 'projects_combine' : ('combine', 'int'),
                         'project_skip' : ('skip', 'int'),
                         'url' : [('url', 'str'), ('urls','list:str')],
                         'name': [('project', 'str'), ('projects','list:str')],
                         'basedir' : [('basedir','str'), ('basedirs', 'list:str')],
                         'verbosity_value' : [('verbosity','int'), ('verbosities','list:int')],
                         'timeout_value' : [('projtimeout','float'),('projtimeouts','list:float')],

                         'proxyserver': ('proxy','str'),
                         'proxyuser': ('puser','str'),
                         'proxypasswd' : ('ppasswd','str'),
                         'proxyport_value' : ('proxyport','int'),

                         'username': ('username','str'),
                         'passwd' : ('passwd','str'),
                         
                         # 'urlserver_status' : ('urlserver','int'),
                         'urlhost' : ('urlhost','str'),
                         'urlport_value' : ('urlport','int'),

                         'html_value' : ('html','int'),
                         'images_value' : ('images','int'),
                         'javascript_value' : ('javascript','int'),
                         'javaapplet_value' : ('javaapplet','int'),
                         'querylinks_value' : ('getquerylinks','int'),

                         'cache_status' : ('pagecache','int'),
                         'datacache_value' : ('datacache','int'),

                         'urllist': ('urlfile', 'str'),
                         'urltreefile' : ('urltreefile', 'str'),
                         'archive_status' : ('archive', 'int'),
                         'archive_format' : ('archformat', 'str'),
                         'urlheaders_status' : ('urlheaders', 'int'),
                         'retries_value': ('retryfailed','int'),
                         'imagelinks_value' : ('getimagelinks','int'),
                         'stylesheetlinks_value' : ('getstylesheets','int'),
                         'offset_start' : ('linksoffsetstart','int'),
                         'offset_end' : ('linksoffsetend','int'),
                         'fetchlevel_value' : ('fetchlevel','int'),
                         'extserverlinks_value' : ('eserverlinks','int'),
                         'extpagelinks_value' : ('epagelinks','int'),
                         'depth_value' : ('depth','int'),
                         'extdepth_value' : ('extdepth','int'),
                         'subdomain_value' : ('subdomain','int'),
                         'maxextservers_value' : ('maxextservers','int'),
                         'maxextdirs_value' : ('maxextdirs','int'),
                         'maxfiles_value' : ('maxfiles','int'),
                         'maxfilesize_value' : ('maxfilesize','int'),
                         'connections_value' : ('connections','int'),
                         'requests_value' : ('requests','int'),
                         'robots_value' : ('robots','int'),
                         'timelimit_value' : ('timelimit','int'),
                         'urlpriority' : ('urlpriority','str'),
                         'serverpriority' : ('serverpriority','str'),
                         'urlfilter': ('urlfilter','str'),
                         'serverfilter' : ('serverfilter','str'),
                         'wordfilter' : ('wordfilter','str'),
                         'junkfilter_value' : ('junkfilter','int'),
                         'workers_status' : ('usethreads','int'),
                         'workers_size' : ('threadpoolsize','int'),
                         'workers_timeout' : ('timeout','float'),
                         'trackers_value' : ('maxtrackers','int'),
                         'trackers_timeout' : ('fetchertimeout','float'),                         
                         'locale' : ('locale','str'),
                         'fastmode_value': ('fastmode','int'),
                         'savesessions_value': ('savesessions','int'),
                         'timegap_value': ('sleeptime', 'float'),
                         'timegap_random': ('randomsleep', 'int'),
                         
                         'simulate_value': ('simulate', 'int'),
                         'localise_value' : ('localise','int'),
                         'browsepage_value' : ('browsepage','int'),

                         'configfile_value': ('configfile', 'str'),
                         'projectfile_value': ('projectfile', 'str'),

                         'urlfilterre_value': (('inclfilter', 'list'),
                                               ('exclfilter', 'list'),
                                               ('allfilters', 'list')),
                         'serverfilterre_value':(('serverinclfilter', 'list'),
                                                 ('serverexclfilter', 'list'),
                                                 ('allserverfilters', 'list')),
                         'urlprioritydict_value': ('urlprioritydict', 'dict'),
                         'serverprioritydict_value': ('serverprioritydict', 'dict'),
                         'http_compress' : ('httpcompress', 'int'),
                         'plugin_name': ('plugins','func:set_plugin')
                         }

    def assign_option(self, option_val, value, kwargs={}):
        """ Assign values to internal variables
        using the option specified """

        # Currently this is used only to parse
        # xml config files.
        if len(option_val) == 2:
            key, typ = option_val
            # If type is not a list, the
            # action is simple assignment

            # Bug fix: If someone has set the
            # value to 'True'/'False' instead of
            # 1/0, convert to bool type first.
            
            if type(value) in (str, unicode):
                if value.lower() == 'true':
                    value = 1
                elif value.lower() == 'false':
                    value = 0

            if typ.find(':') == -1:
                # do any type casting of the option
                fval = (eval(typ))(value)
                self[key] = fval
                
                # If type is list, the action is
                # appending, after doing any type
                # casting of the actual value
            else:
                # Type is of the form <type>:<actual type>
                typname, typ = typ.split(':')
                # print 'typename',typname
                
                if typname == 'list':
                    if typ:
                        fval = (eval(typ))(value)
                    else:
                        fval = value
                        
                    var = self[key]
                    var.append(fval)
                elif typname == 'func':
                    funktion = getattr(self, typ)
                    if funktion:
                        funktion(kwargs)
        else:
            debug('Error in option value %s!' % option_val)

    def set_option(self, option, value, negate=0):
        """ Set the passed option in the config class
        with its value as the passed value """
        
        # find out if the option exists in the dictionary
        if option in self.xml_map.keys():
            # if the option is a string or int or any
            # non-seq type

            # if value is an emptry string, return error
            if value=="": return -1

            # Bug fix: If someone has set the
            # value to 'True'/'False' instead of
            # 1/0, convert to bool type first.
            if type(value) in (str, unicode):
                if value.lower() == 'true':
                    value = 1
                elif value.lower() == 'false':
                    value = 0
            
            if type(value) is not tuple:
                # get the key for the option
                key = (self.xml_map[option])[0]
                # get the type of the option
                typ = (self.xml_map[option])[1]
                # do any type casting of the option
                fval = (eval(typ))(value)
                # do any negation of the option
                if type(fval) in (int,bool):
                    if negate: fval = not fval
                # set the option on the dictionary
                self[key] = fval
                
                return 1
            else:
                # option is a tuple of values
                # iterate through all values of the option
                # see if the size of the value tuple and the
                # size of the values for this key match
                _values = self.xml_map[option]
                if len(_values) != len(value): return -1

                for index in range(0, len(_values)):
                    _v = _values[index]
                    if len(_v) !=2: continue
                    _key, _type = _v

                    v = value[index]
                    # do any type casting on the option's value
                    fval = (eval(_type))(v)
                    # do any negation
                    if type(fval) in (int,bool):                    
                        if negate: fval = not fval
                    # set the option on the dictionary
                    self[_key] = fval

                return 1

        return -1

    def set_option_xml_attr(self, option, value, attrs):
        """ Set an option from the xml config file for an XML attribute """

        # If option in things to be skipped, return
        if option in self.items_to_skip:
            return
        
        option_val = self.xml_map.get(option, None)
        
        if option_val:
            try:
                if type(option_val) is tuple:
                    self.assign_option(option_val, value, attrs)
                elif type(option_val) is list:
                    # If the option_val is a list, there
                    # might be multiple vars to set.
                    for item in option_val:
                        # The item has to be a tuple again...
                        if type(item) is tuple:
                            # Set it
                            self.assign_option(item, value, attrs)
            except Exception, e:
                return  
        else:
            pass

    def set_option_xml(self, option, value):
        """ Set an option from the xml config file """

        # If option in things to be skipped, return
        if option in self.items_to_skip:
            return
        
        option_val = self.xml_map.get(option, None)
        
        if option_val:
            try:
                if type(option_val) is tuple:
                    self.assign_option(option_val, value)
                elif type(option_val) is list:
                    # If the option_val is a list, there
                    # might be multiple vars to set.
                    for item in option_val:
                        # The item has to be a tuple again...
                        if type(item) is tuple:
                            # Set it
                            self.assign_option(item, value)
            except Exception, e:
                return  
        else:
            pass

    def set_plugin(self, plugindict):
        """ Function for setting plugins from config file """

        plugin = plugindict['name']
        enable = int(plugindict['enable'])
        if enable: self.plugins.append(plugin)
        
    def parse_arguments(self):
        """ Parse the command line arguments """

        # This function has 3 return values
        # -1 => no cmd line arguments/invalid cmd line arguments
        # ,so force program to read config file.
        # 0 => existing project file supplied in cmd line
        # 1 => all options correctly read from cmd line

        # if no cmd line arguments, then use config file,
        # return -1
        if len(sys.argv)==1:
            return -1

        # Otherwise parse the arguments, the command line arguments
        # are the same as the variables(dictionary keys) of this class.
        # Description
        # Options needing no arguments
        #
        # -h => prints help
        # -v => prints version info
        
        args, optdict = '',{}
        try:
            if self.appname == 'HarvestMan':
                USAGE = USAGE1
            elif self.appname == 'Hget':
                USAGE = USAGE2
                
            gopt = GenericOptionParser(options.getOptList(self.appname), usage = USAGE % self )
            optdict, args = gopt.parse_arguments()
        except GenericOptionParserError, e:
            sys.exit('Error: ' + str(e))

        # print optdict
        
        cfgfile = False

        if self.appname == 'HarvestMan':
            for option, value in optdict.items():
                # If an option with value of null string, skip it
                if value=='':
                   # print 'Skipping option',option
                   continue
                else:
                   # print 'Processing option',option,'value',value
                   pass

                # first parse arguments with no options
                if option=='version' and value:
                    self.print_version_info()
                    sys.exit(0)                
                elif option=='configfile':
                    if self.check_value(option,value):
                        self.set_option_xml('configfile_value', self.process_value(value))
                        cfgfile = True
                        # Continue parsing and take rest of options from cmd line
                elif option=='projectfile':
                    if self.check_value(option,value):
                        self.set_option_xml('projectfile_value', self.process_value(value))
                        import utils 

                        projector = utils.HarvestManProjectManager()

                        if projector.read_project() == 0:
                            # No need to parse further values
                            return 0


                elif option=='basedir':
                    if self.check_value(option,value): self.set_option_xml('basedir', self.process_value(value))
                    print self.basedir, self.basedirs
                elif option=='project':
                    if self.check_value(option,value): self.set_option_xml('name', self.process_value(value))
                elif option=='retries':
                    if self.check_value(option,value): self.set_option_xml('retries_value', self.process_value(value))
                elif option=='localise':
                    if self.check_value(option,value): self.set_option_xml('localise_value', self.process_value(value))
                elif option=='fetchlevel':
                    if self.check_value(option,value): self.set_option_xml('fetchlevel_value', self.process_value(value))
                elif option=='maxthreads':
                    if self.check_value(option,value): self.set_option_xml('trackers_value', self.process_value(value))
                elif option=='maxfiles':
                    if self.check_value(option,value): self.set_option_xml('maxfiles_value', self.process_value(value))
                elif option=='timelimit':
                    if self.check_value(option,value): self.set_option_xml('timelimit_value', self.process_value(value))
                elif option=='workers':
                    self.set_option_xml('workers_status',1)
                    if self.check_value(option,value): self.set_option_xml('workers_size', self.process_value(value))                
                elif option=='urlfilter':
                    if self.check_value(option,value): self.set_option_xml('urlfilter', self.process_value(value))
                elif option=='depth':
                    if self.check_value(option,value): self.set_option_xml('depth_value', self.process_value(value))
                elif option=='robots':
                    if self.check_value(option,value): self.set_option_xml('robots_value', self.process_value(value))
                elif option=='urllist':
                    if self.check_value(option,value): self.set_option_xml('urllist', self.process_value(value))
                elif option=='proxy':
                    if self.check_value(option,value):
                        # Set proxyencrypted flat to False
                        self.proxyenc=False
                        self.set_option_xml('proxyserver', self.process_value(value))
                elif option=='proxyuser':
                    if self.check_value(option,value): self.set_option_xml('proxyuser', self.process_value(value))                
                elif option=='proxypasswd':
                    if self.check_value(option,value): self.set_option_xml('proxypasswd', self.process_value(value))
                elif option=='urlserver':
                    if self.check_value(option,value): self.set_option_xml('urlserver_status', self.process_value(value))

                elif option=='cache':
                    if self.check_value(option,value): self.set_option_xml('cache_status', self.process_value(value))
                elif option=='connections':
                    if self.check_value(option,value):
                        val = self.process_value(value)
                        if val>=self.connections:
                            self.connections = val + 1
                        self.set_option_xml('requests_value', val)
                elif option=='verbosity':
                    if self.check_value(option,value): self.set_option_xml('verbosity_value', self.process_value(value))
                elif option=='subdomain':
                    if value: self.set_option_xml('subdomain_value', 0)                    
                elif option=='savesessions':
                    if self.check_value(option,value): self.set_option_xml('savesessions_value', self.process_value(value))
                elif option=='simulate':
                    self.set_option_xml('simulate_value', value)
                elif option=='plugins':
                    # Plugin is specified as plugin1+plugin2+...
                    plugins = value.split('+')
                    # Remove any duplicate occurence of same plugin
                    self.plugins = list(set([plugin.strip() for plugin in plugins]))
                    # Don't allow reading plugin from config file now
                    self.items_to_skip.append('plugin_name')

        elif self.appname == 'Hget':
            # Hget options
            for option, value in optdict.items():
                # If an option with value of null string, skip it
                if value=='':
                   # print 'Skipping option',option
                   continue
                else:
                   # print 'Processing option',option,'value',value
                   pass

                # first parse arguments with no options
                if option=='version' and value:
                    self.print_version_info()
                    sys.exit(0)                               
                elif option=='numparts':
                    # Setting numparts forces split downloads
                    self.numparts = abs(int(value))
                    if self.numparts == 0:
                        print 'Error: Invalid value for number of parts, value should be non-zero!'
                        sys.exit(1)
                    if self.numparts > 10:
                        print 'Error: Exceeding the maximum limit (10) of parts, please use a lower setting.'
                        sys.exit(1)
                    if self.numparts>1:
                        self.forcesplit = True
                        # If we are forcesplitting with parts>1, then disable resume automatically
                        print 'Force-split switched on, resuming will be disabled'
                        self.canresume = False
                    else:
                        print 'Warning: Setting numparts to 1 has no effect!'
                elif option=='memory':
                    if value:
                        print 'Warning: Enabling in-memory flag, data will be stored in memory!'
                        self.inmem = True
                elif option=='notempdir':
                    if value:
                        print 'Temporary files will be saved to current directory'
                        # Do not use temporary directory for saving intermediate files
                        self.hgetnotemp = True
                elif option=='output':
                    self.hgetoutfile = value
                elif option=='outputdir':
                    self.hgetoutdir = value
                elif option=='verbose':
                    self.hgetverbose = value
                elif option=='proxy':
                    if self.check_value(option,value):
                        # Set proxyencrypted flat to False
                        self.proxyenc=False
                        self.set_option_xml('proxyserver', self.process_value(value))
                elif option=='proxyuser':
                    if self.check_value(option,value): self.set_option_xml('proxyuser', self.process_value(value))
                elif option=='proxypasswd':
                    if self.check_value(option,value): self.set_option_xml('proxypasswd', self.process_value(value))
                elif option=='passwd':
                    if self.check_value(option,value): self.set_option_xml('passwd', self.process_value(value))
                elif option=='username':
                    if self.check_value(option,value): self.set_option_xml('username', self.process_value(value))
                elif option == 'single':
                    if value:
                        print "Single thread option set, disabling multipart downloads..."
                        self.nomultipart = True
                elif option == 'mirrorfile':
                    filename = value.strip()
                    if os.path.isfile(filename):
                        print 'Mirrors will be loaded from %s...' % filename
                        self.mirrorfile = filename
                    else:
                        print  'Warning: Mirror file %s not found!' % filename
                elif option == 'resumeoff':
                    if value:
                        print 'Resume mode set to off, partial downloads will not be resumed!'
                        self.canresume = False
                    
                    
        # print self.subdomain
        if self.nocrawl:
            self.pagecache = False
            self.rawsave = True
            self.localise = 0
            # Set project name to ''
            self.set_option_xml('name','')
            # Set basedir to dot
            self.set_option_xml('basedir','.')
        
        if args:
            # Any option without an argument is assumed to be a URL
            for arg in args:
                self.set_option_xml('url',self.process_value(arg))
                
            # Since we set a URL from outside, we dont want to read
            # URLs from the config file - same for plugins
            self.items_to_skip = ['url','name','basedir','verbosity_value']

        # print 'URLS=>',self.urls
        # If urlfile option set, read all URLs from a file
        # and load them.
        if self.urlfile:
            if not os.path.isfile(self.urlfile):
                print 'Error: Cannot find URL file %s!' % self.urlfile
                return -1
            # Open file
            try:
                lines = open(self.urlfile).readlines()
                if len(lines):
                    # Reset all...
                    self.urls = []
                    self.projects = []
                    self.projtimeouts = []
                    self.basedirs = []

                    for line in lines:
                        url = line.strip()
                        # Fix URL protocol string
                        url = self._fix_url_protocol(url)
                        try:
                            # Create project name
                            h = urlparser.HarvestManUrlParser(url)
                            self.urls.append(url)
                            project = h.get_domain()
                            self.projects.append(project)
                            self.basedirs.append('.')
                        except urlparser.HarvestManUrlParserError, e:
                            continue

                    # We would now want to skip url, project,
                    # basedir etc in the config file
                    self.items_to_skip = ['url','name','basedir','verbosity_value']

            except Exception, e:
                print e
                return -1


        # print 'URLS=>',self.urls
        # sys.exit(0)
                        
        # Error in option value
        if self._error:
            print self._error, value
            return -1

        # If need to pass config file return -1
        if cfgfile:
            return -1
        
        return 1

    def check_value(self, option, value):
        """ This function checks the values for options
        when options are supplied as command line arguments.
        Returns 0 on any error and non-zero if ok """

        # check #1: If value is a null, return 0
        if not value:
            self._error='Error in option value for option %s, value should not be empty!' % option
            return 0

        # no other checks right now
        return 1

    def process_value(self, value):
        """ This function processes values of command line
        arguments and returns values which can be used by
        this class """

        # a 'yes' is treated as 1 and 'no' as 0
        # also an 'on' is treated as 1 and 'off' as 0
        # Other valid values: integers, strings, 'YES'/'NO'
        # 'OFF'/'ON'

        ret=0
        # We expect the null check has been done before
        val = value.lower()
        if val in ('yes', 'on'):
            return 1
        elif val in ('no', 'off'):
            return 0

        # convert value to int
        try:
            ret=int(val)
            return ret
        except:
            pass

        # return string value directly
        return str(value)

    def print_help(self):
        """ Prints the help information """

        print PROG_HELP % {'appname' : self.appname,
                           'version' : self.version,
                           'maturity' : self.maturity }

    def print_version_info(self):
        """ Print version information """

        print 'Version: %s %s' % (self.version, self.maturity)

    def _fix_url_protocol(self, url):
        """ Fix URL protocol string """
        
        r = re.compile('www\d?\.|http://|https://|ftp://|file://',re.IGNORECASE)
        if not r.match(url):
            # Assume http url
            # prepend http:// to it
            # We prepend http:// to even FTP urls so that
            # the ftp servers can be crawled.
            url = 'http://' + url

        return url
    
    def _fix(self):
        """ Fix errors in config variables """

        # If there is more than one url, we
        # combine all the project related
        # variables into a dictionary for easy
        # lookup.
        num=len(self.urls)
        if num==0:
            msg = 'Fatal Error: No URLs given, Aborting.\nFor command-line options run with -h option'
            sys.exit(msg)

        if not len(self.projtimeouts): self.projtimeouts.append(self.projtimeout)
        if not len(self.verbosities): self.verbosities.append(self.verbosity)

        # Fix urlhost
        if self.urlhost in ('localhost', 'localhost.localdomain','0.0.0.0'):
            self.urlhost = '127.0.0.1'
        
        if num>1:
            # Check the other list variables
            # If their length is less than url length
            # make up for it.
            for x in range(num-len(self.projects)):
                self.projects.append(self.projects[x])
            for x in range(num-len(self.basedirs)):
                self.basedirs.append(self.basedirs[x])                    
            for x in range(num-len(self.verbosities)):
                self.verbosities.append(self.verbosities[x])
            for x in range(num-len(self.projtimeouts)):
                self.projtimeouts.append(self.projtimeouts[x])
                

        # Fix url error
        for x in range(len(self.urls)):
            url = self.urls[x]
            
            # If null url, return
            if not url: continue

            # Fix protocol strings
            url = self._fix_url_protocol(url)
            self.urls[x] = url
            
            # If project is not set, set it to domain
            # name of the url.
            project = None
            try:
                project = self.projects[x]
            except:
                pass

            if not project:
                h = urlparser.HarvestManUrlParser(url)
                project = h.get_domain()
                self.projects.append(project)

            basedir = None
            try:
                basedir = self.basedirs[x]
            except:
                pass

            if not basedir:
                self.basedirs.append('.')

            self.plugins = list(set(self.plugins))
            print 'plugins',self.plugins
            
            if 'swish-e' in self.plugins:
                # Disable any message output for swish-e
                from common.common import SetLogSeverity
                
                self.verbosity = 0
                self.verbosities = [0]*len(self.verbosities)
                SetLogSeverity()

    def parse_config_file(self):
        """ Opens the configuration file and parses it """

        from common.common import logconsole
        
        cfgfile = self.configfile
        if not os.path.isfile(cfgfile):
            logconsole('Configuration file %s not found...' % cfgfile)
            # Try in $HOME/.harvestman/conf directory
            if self.userconfdir:
                cfgfile = os.path.join(self.userconfdir, 'config.xml')
                if os.path.isfile(cfgfile):
                    logconsole('Using configuration file %s...' % cfgfile)
                    self.configfile = cfgfile
                else:
                    logconsole('Configuration file %s not found...' % cfgfile)
        else:
            logconsole('Using configuration file %s...' % cfgfile)
            
        return configparser.parse_xml_config_file(self, cfgfile)
        
    def get_program_options(self):
        """ This function gets the program options from
        the config file or command line """

        # first check in argument list, if failed
        # check in config file
        res = self.parse_arguments()
        if res==-1:
            self.reset_list_params()
            self.parse_config_file()

        # fix errors in config variables
        self._fix()

    def reset_list_params(self):
        pass

    def reset_progress(self):
        self.progressobj = None
        self.progressobj = TextProgress()
        
    def __getattr__(self, name):
        try:
            return self[intern(name)]
        except KeyError:
            return

    def __setattr__(self, name, value):
        self[intern(name)] = value



