#! /usr/bin/env python
# -- coding: latin-1
""" Hget - Extensible, modular, multithreaded Internet
    downloader program in the spirit of wget, using
    HarvestMan codebase, with HTTP multipart support.
    
    Version      - 1.0 beta 1.

    Author: Anand B Pillai <anand at harvestmanontheweb.com>

    HGET is free software. See the file LICENSE.txt for information
    on the terms and conditions of usage, and a DISCLAIMER of ALL WARRANTIES.

 Modification History

    Created: April 19 2007 Anand B Pillai

     April 20 2007 Added more command-line options   Anand
     April 24 2007 Made connector module to flush data  Anand
                   to tempfiles when run with hget.
     April 25 2007 Implementation of hget features is  Anand
                   completed!
     April 30 2007 Many fixes/enhancements to hget.
                   1. Reconnection of a lost connection does not
                   lose already downloaded data.
                   2. Closing of files of threads when download is
                   aborted.
                   3. Thread count shows current number of threads
                   which are actually doing downloads, reflecting
                   the activity.
                   4. Final printing of time taken, average bandwidth
                   and file size.

     May 10 2007   Added support for sf.net mirrors in multipart.
     
Copyright(C) 2007, Anand B Pillai

"""

import sys, os
import re
import shutil
import connector
import urlparser
import config
import logger
import datamgr
import urlthread

from common.common import *
from harvestmanklass import HarvestMan

VERSION='1.0'
MATURITY='beta 1'

class Hget(HarvestMan):
    """ Web getter class for HarvestMan which defines
    a wget like interface for downloading files on the
    command line with HTTP/1.0 Multipart support """

    def grab_url(self, url):
        """ Download URL """

        # Reset progress object
        self._cfg.reset_progress()

        monitor = urlthread.HarvestManUrlThreadPoolMonitor(self._pool)
        monitor.start()
        
        try:
            # print self._cfg.requests, self._cfg.connections
            conn = connector.HarvestManUrlConnector()
            # Set mode to flush/inmem
            conn.set_data_mode(self._pool.get_data_mode())
            
            try:
                print '\nDownloading URL',url,'...'
                urlobj = urlparser.HarvestManUrlParser(url)
                ret = conn.url_to_file(urlobj)
            except urlparser.HarvestManUrlParserError, e:
                print str(e)
                print 'Error: Invalid URL "%s"' % url

        except Exception, e:
            print 'Caught fatal error (%s): %s' % (e.__class__.__name__, str(e))
            self.clean_up(conn, urlobj, e)
        except KeyboardInterrupt, e:
            self.clean_up(conn, urlobj)
            
        monitor.stop()

    def clean_up(self, conn, urlobj, exception=None):

        reader = conn.get_reader()
        if reader: reader.stop()
        if exception==None:
            print '\n\nDownload aborted by user interrupt.'

        # If flushdata mode, delete temporary files
        if self._cfg.flushdata:
            print 'Cleaning up temporary files...'
            fname1 = conn.get_tmpfname()
            fullurl = urlobj.get_full_url()
            range_request = conn._headers.get('accept-ranges','').lower()
            # If server supports range requests, then do not
            # clean up temp file, since we can start from where
            # we left off, if this file is requested again.
            if not range_request=='bytes':
                if fname1:
                    try:
                        os.remove(fname1)
                    except OSError, e:
                        print e
            elif fname1:
                # Dump an info file consisting of the header
                # information to a file, so that we can use it
                # to resume downloading from where we left off
                infof = os.path.join(os.path.dirname(fname1), ''.join((".info#",
                                                                       str(abs(hash(fullurl))))))
                if not os.path.isfile(infof):
                    try:
                        open(infof, 'wb').write(str(conn._headers))
                    except (OSError, IOError), e:
                        print e

            lthreads = self._pool.get_threads()
            lfiles = []
            for t in lthreads:
                fname = t.get_tmpfname()
                if fname: lfiles.append(fname)
                t.close_file()

            print 'Waiting for threads to finish...'
            self._pool.end_all_threads()

            # For currently running multipart download, clean
            # up all pieces since there is no guarantee that
            # the next request will be for the same number of
            # pieces of files, though the server supports
            # multipart downloads.
            if lfiles:
                tmpdir = os.path.dirname(lfiles[0])
            else:
                tmpdir = ''
                
            for f in lfiles:
                if os.path.isfile(f):
                    try:
                        os.remove(f)
                    except (IOError, OSError), e:
                        print 'Error: ',e

            # Commented out because this is giving a strange
            # exception on Windows.
            
            # If doing multipart, cleanup temp dir also
            if self._cfg.multipart:
                if not self._cfg.hgetnotemp and tmpdir:
                    try:
                        shutil.rmtree(tmpdir)
                    except OSError, e:
                        print e
            print 'Done'

        print ''
        
    def create_initial_directories(self):
        """ Create the initial directories for Hget """

        super(Hget, self).create_initial_directories()
        # Create temporary directory for saving files
        if not self._cfg.hgetnotemp:
            try:
                tmp = GetMyTempDir()
                if not os.path.isdir(tmp):
                    os.makedirs(tmp)
                # Could not make tempdir, set hgetnotemp to True
                if not os.path.isdir(tmp):
                    self._cfg.hgetnotemp = True
            except Exception, e:
                pass

    def _prepare(self):
        """ Do the basic things and get ready """

        # Init Config Object
        InitConfig(config.HarvestManStateObject)
        # Initialize logger object
        InitLogger(logger.HarvestManLogger)
        
        SetUserAgent(self.USER_AGENT)

        self._cfg = GetObject('config')
        self._cfg.appname = 'Hget'
        self._cfg.version = VERSION
        self._cfg.maturity = MATURITY
        self._cfg.nocrawl = True
        self._pool = None
        
        # Get program options
        self._cfg.parse_arguments()

        self._cfg.flushdata = not self._cfg.inmem
        # Set number of connections to two plus numparts
        self._cfg.connections = 2*self._cfg.numparts
        # self._cfg.requests = 2*self._cfg.numparts
        # Thread pool size need to be only equal to numparts
        # self._cfg.threadpoolsize = self._cfg.numparts
        # Set verbosity
        # print self._cfg.hgetverbose
        if self._cfg.hgetverbose:
            self._cfg.verbosity=2
            self._cfg.verbosities
        else:
            self._cfg.verbosity = 1

        SetLogSeverity()

        self.register_common_objects()
        self.create_initial_directories()

    def hget(self):
        """ Download all URLs """

        if len(self._cfg.urls)==0:
            print 'Error: No input URL/file given. Run with -h or no arguments to see usage.\n'
            return -1

        dmgr = GetObject('datamanager')
        dmgr.initialize()
        self._pool = dmgr.get_url_threadpool()
            
        for arg in self._cfg.urls:
            # Check if the argument is a file, if so
            # download URLs specified in the file.
            if os.path.isfile(arg):
                # Open it, read URL per line and schedule download
                print 'Input file %s found, scheduling download of URLs...' % arg
                try:
                    for line in file(arg):
                        url = line.strip()
                        print ''
                        self.grab_url(url)
                except IOError, e:
                    print 'Error:',e
                except Exception, e:
                    raise
            else:
                self.grab_url(arg)
        
    def main(self):
        """ Main routine """

        # Add help option if no arguments are given
        if len(sys.argv)<2:
            sys.argv.append('-h')
            
        self._prepare()
        self.hget()
        return 0

if __name__ == "__main__":
    h = Hget()
    h.main()
    
