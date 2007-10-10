""" mirrors.py - Module which provides support for managing
mirrors for domains, for hget.

Author - Anand B Pillai <anand at harvestmanontheweb.com>

Created,  Anand B Pillai 14/08/07.
Modified  Anand B Pillai 10/10/07  Added file mirror support

Copyright (C) 2007 Anand B Pillai.
    
"""

import random
import urlparser
from common.common import *

SOURCEFORGE = False

SFMIRRORS = ['http://umn.dl.sourceforge.net','http://jaist.dl.sourceforge.net',
             'http://mesh.dl.sourceforge.net','http://superb-west.dl.sourceforge.net',
             'http://superb-east.dl.sourceforge.net','http://keihanna.dl.sourceforge.net',
             'http://optusnet.dl.sourceforge.net','http://kent.dl.sourceforge.net',
             'http://ufpr.dl.sourceforge.net','http://ovh.dl.sourceforge.net',
             'http://switch.dl.sourceforge.net','http://nchc.dl.sourceforge.net',
             'http://heanet.dl.sourceforge.net','http://surfnet.dl.sourceforge.net',
             'http://easynews.dl.sourceforge.net','http://belnet.dl.sourceforge.net',
             'http://puzzle.dl.sourceforge.net','http://internap.dl.sourceforge.net']

# List of mirror URLs loaded from a mirror file/other source
MIRRORS = []

def load_mirrors():
    """ Load mirror information from the mirror file """

    global MIRRORS
    
    cfg = GetObject('config')
    if cfg.mirrorfile:
        for line in file(cfg.mirrorfile):
            url = line.strip()
            if url != '':
                MIRRORS.append(url)
    
def mirrors_available(urlobj):

    flag = False

    if is_sourceforge_url(urlobj):
        global SOURCEFORGE
        SOURCEFORGE = True
        flag = True

    elif len(MIRRORS):
        # See if any MIRRORS are defined
        flag = True
            
    return flag

def log_mirror_message():

    if SOURCEFORGE:
        logconsole('Sourceforge URL found - Splitting download across sourceforge.net mirrors...\n')

def get_mirrors():
    """ Return a list of mirrors for the current server """

    if SOURCEFORGE:
        return SFMIRRORS
    else:
        return MIRRORS
    
def is_multipart_download_supported(urlobj):
    """ Check whether this URL (server) supports multipart downloads """

    return is_sourceforge_url(urlobj)

def is_sourceforge_url(urlobj):
    """ Is this a download from sourceforge ? """

    return (urlobj.domain in ('downloads.sourceforge.net', 'prdownloads.sourceforge.net') or \
           urlobj.get_full_domain() in SFMIRRORS )

def create_multipart_urls(urlobj, numparts):

    urlobjects = []
    relpath = ''

    if SOURCEFORGE:
        # Get relative path of the URL w.r.t root
        relpath = urlobj.get_relative_url()
        relpath = 'sourceforge' + relpath

    elif MIRRORS:
        # Get relative path of the URL w.r.t root        
        relpath = urlobj.get_relative_url()
        
    # Get a random list of servers
    sf = random.sample(get_mirrors(), numparts)
    orig_url = urlobj.get_full_url()
    
    for x in range(numparts):
        # urlobjects.append(copy.deepcopy(urlobj))
        newurlobj = urlparser.HarvestManUrlParser(relpath,baseurl=sf[x])
        # Set mirror_url attribute
        newurlobj.mirror_url = orig_url
        print "Mirror URL %d=> %s" % (x+1, newurlobj.get_full_url())
        urlobjects.append(newurlobj)

    return urlobjects
    
def download_multipart_url(urlobj, clength, numparts, threadpool):
    """ Download URL multipart from supported servers """

    log_mirror_message()
    
    # List of servers - note that we are not doing
    # any kind of search for the nearest servers. Instead
    # a random list is created.
    # Calculate size of each piece
    piecesz = clength/numparts

    # Calculate size of each piece
    pcsizes = [piecesz]*numparts
    # For last URL add the reminder
    pcsizes[-1] += clength % numparts 
    # Create a URL object for each and set range
    urlobjects = create_multipart_urls(urlobj, numparts)

    prev = 0

    for x in range(numparts):
        curr = pcsizes[x]
        next = curr + prev
        urlobject = urlobjects[x]
        urlobject.trymultipart = True
        urlobject.clength = clength
        urlobject.range = xrange(prev, next)
        urlobject.mindex = x
        prev = next

        # Push this URL objects to the pool
        threadpool.push(urlobject)

    return 0


