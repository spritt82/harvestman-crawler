#!/usr/bin/env python
# -- coding: latin-1

# Author: Anand B Pillai <anand at harvestmanontheweb.com>

# genconfig.py - Script to generate config file for
# HarvestMan Program.

# Author - Anand B Pillai.
# Feb 10 2004  Anand      1.3.1 bug fix release.
# Jun 14 2004  Anand      1.3.9 release.
# Sep 23 2004  Anand      1.4 development.
# May 23 2005  Anand      1.4.5 version.

# Copyright(C) 2004-2005, Anand B Pillai.

import sys
import os

class GenConfig(object):

    def __init__(self):

        # Locate HarvestMan modules
        import config
        
        self.__dict__['cfg'] = config.HarvestManStateObject()
        
    def __getattr__(self, name):
        try:
            return self.cfg[name]
        except KeyError:
            return None
        
    def __setattr__(self, name, value):
        self.cfg[name] = value

    def fitString(self, s, field=35):
        return s.ljust(field)
    
    def GenConfigFile(self):

        print ''
        print 'Generating config file...'

        if self.format=='xml':
            filename = 'config.xml'
        elif self.format=='text':
            filename = 'config.txt'
            
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except OSError, e:
                print e
                return
        try:
            cf=open(filename,'w')
            if self.format=='xml':
                self.GenXmlConfigFile(cf)
            elif self.format=='text':
                self.GenTextConfigFile(cf)
                
        except (IOError, OSError), e:
            print e
            return

    def GenTextConfigFile(self, cf):
        """ Generate config file in text format """

        from common import bin_crypt
        
        # write values
        cf.write(';;HarvestMan Configuration File version 2.0\n\n')
        sys.stdout.write('.....')
        cf.write(';;project related variables\n')
        cf.write(self.fitString('project.url') + str(self.url) + '\n')
        cf.write(self.fitString('project.name') + str(self.project) + '\n')
        cf.write(self.fitString('project.basedir') + str(self.basedir) + '\n')
        cf.write(self.fitString('project.verbosity') + str(self.verbosity) + '\n')
        cf.write(self.fitString('project.timeout') + str(self.projtimeout) + '\n\n')
        
        sys.stdout.write('.....')
        cf.write(';;network related variables\n')
        if self.proxy:
            cf.write(self.fitString('network.proxyserver') + bin_crypt(self.proxy) + '\n')
            cf.write(self.fitString('network.proxyport') + str(self.proxyport) + '\n')
        if self.puser:
            cf.write(self.fitString('network.proxyuser') + bin_crypt(self.puser) + '\n')
        if self.ppasswd:
            cf.write(self.fitString('network.proxypasswd') + bin_crypt(self.ppasswd) + '\n')
        cf.write(self.fitString('network.urlserver') + str(int(self.urlserver)) + '\n')
        cf.write(self.fitString('network.urlport') + str(self.urlport) + '\n')            
        
        cf.write('\n')
        cf.write(';;url related variables\n')
        if self.siteusername:
            cf.write(self.fitString('url.username') + bin_crypt(self.siteusername) + '\n')
        if self.sitepasswd:
            cf.write(self.fitString('url.password') + bin_crypt(self.sitepasswd) + '\n')
        cf.write('\n')

        sys.stdout.write('..........')
        cf.write(';;download related variables\n')

        cf.write(self.fitString('download.html') + str(self.html) + '\n')
        cf.write(self.fitString('download.images') + str(self.images) + '\n')
        cf.write(self.fitString('download.javascript') + str(int(self.javascript)) + '\n')
        cf.write(self.fitString('download.javaapplet') + str(int(self.javaapplet)) + '\n')
        cf.write(self.fitString('download.forms') + str(int(self.getqueryforms)) + '\n')
        cf.write(self.fitString('download.cookies') + str(int(self.cookies)) + '\n')
        
        cf.write(self.fitString('download.cache') + str(int(self.pagecache)) + '\n')
        cf.write(self.fitString('download.datacache') + str(int(self.datacache)) + '\n')
        cf.write(self.fitString('download.retries') + str(int(self.retryfailed)) + '\n')

        sys.stdout.write('....................')
        cf.write(';;download control variables\n')
        cf.write(self.fitString('control.imagelinks') + str(int(self.getimagelinks)) + '\n')
        cf.write(self.fitString('control.stylesheetlinks') + str(int(self.getstylesheets)) + '\n')
        cf.write(self.fitString('control.fetchlevel') + str(self.fetchlevel) + '\n')
        cf.write(self.fitString('control.extserverlinks') + str(int(self.eserverlinks)) + '\n')
        cf.write(self.fitString('control.extpagelinks') + str(int(self.epagelinks)) + '\n')
        cf.write(self.fitString('control.depth') + str(self.depth) + '\n')
        cf.write(self.fitString('control.extdepth') + str(self.extdepth) + '\n')
        cf.write(self.fitString('control.subdomain') + str(int(self.subdomain)) + '\n')
        
        cf.write(self.fitString('control.maxextservers') + str(self.maxextservers) + '\n')
        cf.write(self.fitString('control.maxextdirs') + str(self.maxextdirs) + '\n')
        cf.write(self.fitString('control.maxfiles') + str(self.maxfiles) + '\n')
        cf.write(self.fitString('control.maxfilesize') + str(self.maxfilesize) + '\n')
        cf.write(self.fitString('control.connections') + str(self.connections) + '\n')
        cf.write(self.fitString('control.requests') + str(self.requests) + '\n')
        cf.write(self.fitString('control.timelimit') + str(self.timelimit) + '\n')

        cf.write(self.fitString('control.robots') + str(int(self.robots)) + '\n')
        cf.write(self.fitString('control.urlpriority') + str(self.urlpriority) + '\n')
        cf.write(self.fitString('control.serverpriority') + str(self.serverpriority) + '\n')
        
        cf.write(self.fitString('control.urlfilter') + str(self.urlfilter) + '\n')
        cf.write(self.fitString('control.serverfilter') + str(self.serverfilter) + '\n')
        cf.write(self.fitString('control.wordfilter') + str(self.wordfilter) + '\n')        
        cf.write(self.fitString('control.junkfilter') + str(int(self.junkfilter)) + '\n\n')        


        sys.stdout.write('......')
        cf.write(';;system related variables\n')
        cf.write(self.fitString('system.workers') + str(int(self.usethreads)) + '\n')
        cf.write(self.fitString('system.threadtimeout') + str(self.timeout) + '\n')
        cf.write(self.fitString('system.threadpoolsize') + str(self.threadpoolsize) + '\n')
        
        cf.write(self.fitString('system.trackers') + str(self.maxtrackers) + '\n')
        cf.write(self.fitString('system.locale') + str(self.locale) + '\n')        
        cf.write(self.fitString('system.fastmode') + str(int(self.fastmode)) + '\n\n')

        sys.stdout.write('..')
        cf.write(';;indexer related variables\n')
        cf.write(self.fitString('indexer.localise') + str(int(self.localise)) + '\n\n')

        sys.stdout.write('....')
        cf.write(';;files related variables\n')
        cf.write(self.fitString('files.urlslistfile') + str(self.urlslistfile) + '\n')
        cf.write(self.fitString('files.urltreefile') + str(self.urltreefile) + '\n\n')
        cf.write(self.fitString('files.archive') + str(self.archive) + '\n')
        cf.write(self.fitString('files.archformat') + str(self.archformat) + '\n')
        cf.write(self.fitString('files.urlheaders') + str(self.urlheaders) + '\n')
        cf.write(self.fitString('files.urlheaderformat') + str(self.urlheadersformat) + '\n\n')                
        sys.stdout.write('..')
        cf.write(';;display related variables\n')
        cf.write(self.fitString('display.browsepage') + str(int(self.browsepage)) + '\n\n')

        cf.close()
        print "\nWrote file 'config.txt'."

    def GenXmlConfigFile(self, cf):
        """ Generate config file in xml format """

        from common import bin_crypt
        
        # Write xml PI
        cf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        cf.write('<!DOCTYPE HarvestMan SYSTEM "HarvestMan.dtd">\n')
        # HarvestMan element
        cf.write('<HarvestMan>\n')
        # config element
        cf.write('\t<config version="3.0" xmlversion="1.0">\n\n')
        # project node
        cf.write('\t\t<project skip="0">\n')
        cf.write("".join(('\t\t\t<url>',self.url,'</url>\n')))
        cf.write("".join(('\t\t\t<name>',self.project,'</name>\n')))
        cf.write("".join(('\t\t\t<basedir>',self.basedir,'</basedir>\n')))
        cf.write("".join(('\t\t\t<verbosity value="',str(self.verbosity),'"/>\n')))
        cf.write("".join(('\t\t\t<timeout value="',str(self.projtimeout),'"/>\n')))
        # end of project node
        cf.write('\t\t</project>\n\n')

        # network node
        cf.write('\t\t<network>\n')
        # proxy
        cf.write('\t\t\t<proxy>\n')
        cf.write("".join(('\t\t\t\t<proxyserver>',bin_crypt(self.proxy),'</proxyserver>\n')))
        cf.write("".join(('\t\t\t\t<proxyuser>',bin_crypt(self.puser),'</proxyuser>\n')))
        cf.write("".join(('\t\t\t\t<proxypasswd>',bin_crypt(self.ppasswd),'</proxypasswd>\n')))
        cf.write("".join(('\t\t\t\t<proxyport value="',str(self.proxyport),'"/>\n')))        
        cf.write('\t\t\t</proxy>\n')
        # url server
        cf.write("".join(('\t\t\t<urlserver status="',str(self.urlserver),'">\n')))
        cf.write("".join(('\t\t\t\t<urlhost>',self.urlhost,'</urlhost>\n')))
        cf.write("".join(('\t\t\t\t<urlport value="',str(self.urlport),'"/>\n')))
        cf.write('\t\t\t</urlserver>\n')
        # end of network node
        cf.write('\t\t</network>\n\n')

        # download node
        cf.write('\t\t<download>\n')
        # types
        cf.write('\t\t\t<types>\n')
        cf.write("".join(('\t\t\t\t<html value="',str(self.html),'"/>\n')))
        cf.write("".join(('\t\t\t\t<images value="',str(self.images),'"/>\n')))
        cf.write("".join(('\t\t\t\t<javascript value="',str(self.javascript),'"/>\n')))
        cf.write("".join(('\t\t\t\t<javaapplet value="',str(self.javaapplet),'"/>\n')))
        cf.write("".join(('\t\t\t\t<forms value="',str(self.getqueryforms),'"/>\n')))
        cf.write("".join(('\t\t\t\t<cookies value="',str(self.cookies),'"/>\n')))
        cf.write('\t\t\t</types>\n')
        # cache
        cf.write("".join(('\t\t\t<cache status="',str(self.pagecache),'">\n')))
        cf.write("".join(('\t\t\t\t<datacache value="',str(self.datacache),'"/>\n')))
        cf.write('\t\t\t</cache>\n')
        # misc
        cf.write('\t\t\t<misc>\n')
        cf.write("".join(('\t\t\t\t<retries value="',str(self.retryfailed),'"/>\n')))
        cf.write('\t\t\t</misc>\n')
        # end of download node
        cf.write('\t\t</download>\n\n')

        # control node
        cf.write('\t\t<control>\n')
        # links
        cf.write('\t\t\t<links>\n')
        cf.write("".join(('\t\t\t\t<imagelinks value="', str(self.getimagelinks), '"/>\n')))
        cf.write("".join(('\t\t\t\t<stylesheetlinks value="', str(self.getstylesheets), '"/>\n')))
        cf.write('\t\t\t</links>\n')
        # extent
        cf.write('\t\t\t<extent>\n')
        cf.write("".join(('\t\t\t\t<fetchlevel value="', str(self.fetchlevel), '"/>\n')))
        cf.write("".join(('\t\t\t\t<extserverlinks value="', str(self.eserverlinks), '"/>\n')))
        cf.write("".join(('\t\t\t\t<extpagelinks value="', str(self.epagelinks), '"/>\n')))
        cf.write("".join(('\t\t\t\t<depth value="', str(self.depth), '"/>\n')))
        cf.write("".join(('\t\t\t\t<extdepth value="', str(self.extdepth), '"/>\n')))
        cf.write("".join(('\t\t\t\t<subdomain value="', str(self.subdomain), '"/>\n')))                
        cf.write('\t\t\t</extent>\n')
        # limits
        cf.write('\t\t\t<limits>\n')
        cf.write("".join(('\t\t\t\t<maxextservers value="', str(self.maxextservers), '"/>\n')))
        cf.write("".join(('\t\t\t\t<maxextdirs value="', str(self.maxextdirs), '"/>\n')))
        cf.write("".join(('\t\t\t\t<maxfiles value="', str(self.maxfiles), '"/>\n')))
        cf.write("".join(('\t\t\t\t<maxfilesize value="', str(self.maxfilesize), '"/>\n')))
        cf.write("".join(('\t\t\t\t<connections value="', str(self.connections), '"/>\n')))
        cf.write("".join(('\t\t\t\t<requests value="', str(self.requests), '"/>\n')))
        cf.write("".join(('\t\t\t\t<timelimit value="', str(self.timelimit), '"/>\n')))        
        cf.write('\t\t\t</limits>\n')
        # rules
        cf.write('\t\t\t<rules>\n')
        cf.write("".join(('\t\t\t\t<robots value="', str(self.robots), '"/>\n')))
        cf.write("".join(('\t\t\t\t<urlpriority>', str(self.urlpriority), '</urlpriority>\n')))
        cf.write("".join(('\t\t\t\t<serverpriority>', str(self.serverpriority), '</serverpriority>\n')))
        cf.write('\t\t\t</rules>\n')
        # filters
        cf.write('\t\t\t<filters>\n')
        cf.write("".join(('\t\t\t\t<urlfilter>', str(self.urlfilter), '</urlfilter>\n')))
        cf.write("".join(('\t\t\t\t<serverfilter>', str(self.serverfilter), '</serverfilter>\n')))
        cf.write("".join(('\t\t\t\t<wordfilter>', str(self.wordfilter), '</wordfilter>\n')))
        cf.write("".join(('\t\t\t\t<junkfilter value="', str(self.junkfilter), '"/>\n')))
        cf.write('\t\t\t</filters>\n')
        # end of control node
        cf.write('\t\t</control>\n\n')

        # system node
        cf.write('\t\t<system>\n')
        cf.write("".join(('\t\t\t<workers status="',str(self.usethreads),'" size="',str(self.threadpoolsize),
                          '" timeout="',str(self.timeout),'"/>\n')))
        cf.write("".join(('\t\t\t<trackers value="',str(self.maxtrackers),'"/>\n')))
        cf.write("".join(('\t\t\t<locale>',str(self.locale),'</locale>\n')))
        cf.write("".join(('\t\t\t<fastmode value="',str(self.fastmode),'"/>\n')))
        # end of system node
        cf.write('\t\t</system>\n\n')
        
        # files node
        cf.write('\t\t<files>\n')
        cf.write("".join(('\t\t\t<urllistfile>',self.urlslistfile,'</urllistfile>\n')))
        cf.write("".join(('\t\t\t<urltreefile>',self.urltreefile,'</urltreefile>\n')))
        cf.write("".join(('\t\t\t<archive status="',str(self.archive),'" format="',str(self.archformat),'"/>\n')))
        cf.write("".join(('\t\t\t<urlheaders status="',str(self.urlheaders),'" format="',str(self.urlheadersformat),'"/>\n')))
        cf.write('\t\t</files>\n\n')

        # indexer node
        cf.write('\t\t<indexer>\n')
        cf.write("".join(('\t\t\t<localise value="',str(self.localise),'"/>\n')))
        cf.write('\t\t</indexer>\n')

        # display node
        cf.write('\t\t<display>\n')
        cf.write("".join(('\t\t\t<browsepage value="',str(self.browsepage),'"/>\n')))
        cf.write('\t\t</display>\n\n')

        # end of config node
        cf.write('\t</config>\n\n')

        # end of HarvestMan node
        cf.write('</HarvestMan>\n')

        cf.close()
        print '\nWrote file config.xml.'
        
    def MakeStringQuery(self, query, strict=1,default=""):

        res=''
        if not strict:
            res=raw_input(query)
        
        while res=='' and strict:
            res=raw_input(query)
            if res=='':
                print 'You need to enter a valid string!'

        if res=='':
            if default:
                print '(Using default value',"".join(("'",str(default),"'")),')'
        elif res==" ":
            # Abort signalled using <space> key
            # generate the config file
            print '<Space> key pressed! '
            print 'Aborting dialog...'
            self.GenConfigFile()
            
        return res

    def MakeYesOrNoQuery(self, query, expected=1):

        res='*'
        yornquery = query + ' [y/n] ? '
        while res !='y' and res != 'n' and res != '' and res != " ":
            res=raw_input(yornquery)
            if res!='y' and res != 'n' and res != '' and res !=" ":
                print 'Please enter y, n or <Enter>.'
            elif res==' ':
                # Abort signalled using <space> key
                # generate the config file
                print '<Space> key pressed! '
                print 'Aborting dialog...'
                self.GenConfigFile()            

        if res=='y': return 1
        elif res=='n': return 0
        elif res=='':
            if expected==1:
                print '(Using default value [y])'
            elif expected==0:
                print '(Using default value [n])'
            else:
                print '(Using default value',str(expected),')'                
            return expected
            
    def UserDialog(self):

        print 'You are about to create a config file for the "HarvestMan" program.'
        print 'You will be asked questions to which you can answer yes or no'
        print 'and questions for which you need to type a response string.'
        print ''
        print 'If you press the [Enter] key for any question, the default value of'
        print 'its setting will be used. If you want to discontinue at any time,'
        print 'press the <space> key as the answer to a question. (If you abort,'
        print 'the program will assume default values for the rest of the options.)'
        print ''
        res=self.MakeYesOrNoQuery('Do you want to continue')
        if res==0: return 0

        self.project=self.MakeStringQuery('Enter the name of this HarvestMan project: ')
        self.url=self.MakeStringQuery('Enter the starting url for this project: ')
        self.basedir=self.MakeStringQuery('Enter the base directory : ')
        self.images=self.MakeYesOrNoQuery('Download images')
        self.html=self.MakeYesOrNoQuery('Download html pages')
        self.getimagelinks=self.MakeYesOrNoQuery('Always get images linked from a page')
        self.getstylesheets=self.MakeYesOrNoQuery('Always get stylesheets associated to a page')        
        proxy=self.MakeYesOrNoQuery('Do you connect to internet through a proxy server', 0)
        if proxy:
            server=self.MakeStringQuery('Enter your proxy server\'s name/ip: ')
            port=self.MakeStringQuery('Enter the proxy port: ', 0, '80')
            if not port:
                port=80
            else:
                port=int(port)
            # change for version 1.1 (port is specified separately)
            self.proxy=server
            self.proxyport=port
            auth=self.MakeYesOrNoQuery('Does your proxy need authentication', 0)
            if auth:
                self.puser=self.MakeStringQuery('Enter Proxy Username: ')
                try:
                    import getpass
                    self.ppasswd=getpass.getpass('Enter Proxy Password: ')
                except:
                    self.ppasswd=self.MakeStringQuery('Enter Proxy Password: ')

        # Locale stuff
        self.locale = self.MakeStringQuery('Locale setting, if any (default is american): ', 0, str(self.locale))
        # Cookie stuff

        # Javascript/java stuff
        self.javascript = self.MakeYesOrNoQuery('Fetch javascripts')
        self.javaapplet = self.MakeYesOrNoQuery('Download java applets')
        
        self.usethreads=self.MakeYesOrNoQuery('Use worker (downloader) threads')
        maxconn=self.MakeStringQuery("Maximum number of simultaneous network connections (default 5): ", 0, str(self.connections))
        if maxconn:
            self.connections=int(maxconn)
        maxreq=self.MakeStringQuery("Maximum number of simultaneous requests to a server (default 5): ", 0, str(self.requests))
        if maxreq: self.requests = int(maxreq)
        self.rep=self.MakeYesOrNoQuery('Obey Robot Exclusion Principle')
        depth=self.MakeStringQuery('Depth of url rel. to starting directory (default is 10) : ', 0, str(self.depth))
        if depth: self.depth=int(depth)

        self.junkfilter=self.MakeYesOrNoQuery('Enable the advertisement/banner filter')
        filter=self.MakeYesOrNoQuery('Filter Urls', 0)
        if filter:
            self.urlfilter=self.MakeStringQuery('Enter/Paste url filter regular expression here: ', 0, str(self.urlfilter))
        sfilter=self.MakeYesOrNoQuery('Filter External Servers', 0)
        if sfilter:
            self.serverfilter=self.MakeStringQuery('Enter/Paste server filter regular expression here: ', 0, str(self.serverfilter))
        priority1= self.MakeYesOrNoQuery('Apply user priorities for urls',0)
        if priority1:
            self.urlpriority=self.MakeStringQuery('Enter/Paste url priority string here:', 0)
        priority2= self.MakeYesOrNoQuery('Apply  priorities for servers',0)
        if priority2:
            self.serverpriority=self.MakeStringQuery('Enter/Paste server priority string here:', 0, str(self.serverpriority))   
        self.retry=self.MakeYesOrNoQuery('Retry failed links')
        self.subdomain=self.MakeYesOrNoQuery('Consider subdomains in web servers as external servers', 0)
        self.getqueryforms=self.MakeYesOrNoQuery('Skip server-side query forms', 1)
        
        if self.MakeYesOrNoQuery('Localise links in Downloaded Files'):
            if self.MakeYesOrNoQuery('Localise links using absolute path names', 2) == 1:
                self.localise=1
        else:
            self.localise=0

        prjtimeout = self.MakeStringQuery("Timeout value in seconds for the project ", 0, str(self.projtimeout))
        if prjtimeout:
            self.projtimeout = float(prjtimeout)
        self.pagecache = self.MakeYesOrNoQuery('Enable support for page caching')
        if self.pagecache:
            self.datacache = self.MakeYesOrNoQuery('Cache data for files')
        self.browsepage=self.MakeYesOrNoQuery('Add project information to the browse page')
        
        maxfiles=self.MakeStringQuery('Enter maximum number of files to download : ', 0, str(self.maxfiles))
        if maxfiles:
            self.maxfiles=int(maxfiles)
        maxfilesz=self.MakeStringQuery('Specify a maximum file size (default is 1 MB):', 0)
        if maxfilesz: self.maxfilesize=int(maxfilesz)
        dumpurls=self.MakeYesOrNoQuery('Dump crawled urls to a file', 0)
        if dumpurls:
            urlslistfile=self.MakeStringQuery('Url list filename: ', 0, str(self.urlslistfile))
            if urlslistfile: self.urlslistfile=urllistfile
        dumpurltree=self.MakeYesOrNoQuery('Dump a tree of urls (with parent-child relationship)', 0)
        if dumpurltree:
            urltreefile=self.MakeStringQuery('Url tree filename: ', 0, str(self.urltreefile))
            if urltreefile: self.urltreefile = urltreefile
        # Url server - New in 1.4
        self.urlserver=self.MakeYesOrNoQuery("Use the asynchronous url server (instead of queue) ?",0)
        if self.urlserver:
            urlport=self.MakeStringQuery("Specify the port where the url server will listen for requests (default: 3081)",0, str(self.urlport))
            if urlport: self.urlport = int(urlport)
            else: self.urlport = 3081
            
        fetchlevel=self.MakeStringQuery('Which fetch level would you like to set (0,1,2,3 or 4): ', 0, str(self.fetchlevel))
        if fetchlevel:
            self.fetchlevel=int(fetchlevel)
        if self.fetchlevel==1:
            maxextpagelinks=self.MakeStringQuery('Limit of number of external directories: ', 0, str(self.maxextdirs))
            if maxextpagelinks: self.maxextdirs=int(maxextpagelinks)
            edepth=self.MakeStringQuery('Depth of external directories : ', 0, str(self.extdepth))
            if edepth: self.extdepth=int(edepth)
        elif self.fetchlevel>1:
            maxextserverlinks=self.MakeStringQuery('Limit on number of external servers: ', 0, str(self.maxextservers))
            if maxextserverlinks: self.maxextservers=int(maxextserverlinks)
            edepth=self.MakeStringQuery('Depth of external urls (relative to base server): ', 0, str(self.extdepth))
            if edepth: self.extdepth=int(edepth)

        self.archive=int(self.MakeYesOrNoQuery("Archive downloaded files",0))
        if self.archive:
            self.archformat = self.MakeStringQuery("Archive format: [bzip/gzip]", 0)
        self.urlheaders = int(self.MakeYesOrNoQuery("Dump url headers",0))
        timelimit=self.MakeYesOrNoQuery("Do you want to specify a time limit for the project", 0)
        if timelimit:
            self.timelimit=int(self.MakeStringQuery("Time limit for the project (in seconds)"))
        verb=self.MakeStringQuery('Verbosity level (0 - 5, 0 -> minimal messages to 5-> maximum messages) : ',0, str(self.verbosity))
        if verb: self.verbosity=int(verb)

        format = int(self.MakeStringQuery("Config file format, type 1 for text and 2 for xml: "))
        if format==1:
            self.format = 'text'
        elif format==2:
            self.format = 'xml'
        
        return 1


if __name__=="__main__":
    
    import sys
    # Pick up modules from the
    # parent directory.
    sys.path.append("..")
    from common import *
    
    configer=GenConfig()
    try:
        if configer.UserDialog():
            configer.GenConfigFile()
            print 'You are ready to run HarvestMan using your new config file.'
        else:
            print 'Aborting...'
    except KeyboardInterrupt:
        print '\n***User aborted***'
    
        
            
            


