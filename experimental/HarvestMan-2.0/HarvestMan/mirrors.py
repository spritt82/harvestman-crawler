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

sfmirrors = ['http://umn.dl.sourceforge.net','http://jaist.dl.sourceforge.net',
             'http://mesh.dl.sourceforge.net','http://superb-west.dl.sourceforge.net',
             'http://superb-east.dl.sourceforge.net','http://keihanna.dl.sourceforge.net',
             'http://optusnet.dl.sourceforge.net','http://kent.dl.sourceforge.net',
             'http://ufpr.dl.sourceforge.net','http://ovh.dl.sourceforge.net',
             'http://switch.dl.sourceforge.net','http://nchc.dl.sourceforge.net',
             'http://heanet.dl.sourceforge.net','http://surfnet.dl.sourceforge.net',
             'http://easynews.dl.sourceforge.net','http://belnet.dl.sourceforge.net',
             'http://puzzle.dl.sourceforge.net','http://internap.dl.sourceforge.net']

# List of mirror URLs loaded from a mirror file/other source
mymirrors = []

# List of current mirrors in use
current_mirrors = []

def load_mirrors():
    """ Load mirror information from the mirror file """

    global mymirrors
    
    cfg = GetObject('config')
    if cfg.mirrorfile:
        for line in file(cfg.mirrorfile):
            url = line.strip()
            if url != '':
                mymirrors.append(url)
    
def mirrors_available(urlobj):
    return (is_sourceforge_url(urlobj) or len(mymirrors))

def is_multipart_download_supported(urlobj):
    """ Check whether this URL (server) supports multipart downloads """

    return is_sourceforge_url(urlobj)

def is_sourceforge_url(urlobj):
    """ Is this a download from sourceforge ? """

    return (urlobj.domain in ('downloads.sourceforge.net', 'prdownloads.sourceforge.net') or \
           urlobj.get_full_domain() in sfmirrors )

def get_mirrors(urlobj):

    if is_sourceforge_url(urlobj):
        return sfmirrors
    elif mymirrors:
        return mymirrors
    
def create_multipart_urls(urlobj, numparts):

    urlobjects = []
    relpath = ''

    if is_sourceforge_url(urlobj):
        # Get relative path of the URL w.r.t root
        relpath = urlobj.get_relative_url()
        relpath = 'sourceforge' + relpath
        mirrors = sfmirrors

    elif mymirrors:
        # Get relative path of the URL w.r.t root        
        relpath = urlobj.get_relative_url()
        mirrors = mymirrors
        
    # Get a random list of servers
    global current_mirrors
    current_mirrors = random.sample(mirrors, numparts)
    
    orig_url = urlobj.get_full_url()
    
    for x in range(numparts):
        # urlobjects.append(copy.deepcopy(urlobj))
        newurlobj = urlparser.HarvestManUrlParser(relpath,baseurl=current_mirrors[x])
        # Set mirror_url attribute
        newurlobj.mirror_url = urlobj
        # Set another attribute indicating the mirror is different
        newurlobj.mirrored = True
        print "Mirror URL %d=> %s" % (x+1, newurlobj.get_full_url())
        urlobjects.append(newurlobj)

    return urlobjects
    
def download_multipart_url(urlobj, clength, numparts, threadpool):
    """ Download URL multipart from supported servers """

    logconsole('Splitting download across mirrors...\n')
    
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

def get_different_mirror():

    # Remove current mirrors from existing mirrors
    pass

def get_different_mirror_url(urlobj):

    global current_mirrors
    
    mirrors = get_mirrors(urlobj)
    # Get the difference of the 2 sets
    newmirrors = list(set(mirrors).difference(set(current_mirrors)))
    # print 'New mirrors=>',newmirrors
    
    # Get a random one out of it...
    new_mirror = random.sample(newmirrors, 1)[0]
    # Remove the old mirror and replace it with new mirror in
    # current_mirrors
    if new_mirror:
        current_mirrors.remove(urlobj.baseurl.origurl)
        current_mirrors.append(new_mirror)
    else:
        return None
            
    orig_urlobj = urlobj.mirror_url
    
    if is_sourceforge_url(orig_urlobj):
        # Get relative path of the URL w.r.t root
        relpath = orig_urlobj.get_relative_url()
        relpath = 'sourceforge' + relpath
    else:
        # Get relative path of the URL w.r.t root        
        relpath = orig_urlobj.get_relative_url()

    newurlobj = urlparser.HarvestManUrlParser(relpath,baseurl=new_mirror)
    # Set mirror_url attribute
    newurlobj.mirror_url = orig_urlobj
    # Set another attribute indicating the mirror is different
    newurlobj.mirrored = True
    newurlobj.trymultipart = True
    newurlobj.clength = urlobj.clength
    newurlobj.range = urlobj.range
    newurlobj.mindex = urlobj.mindex
    print "New Mirror URL => %s" % newurlobj.get_full_url()
    
    return newurlobj
