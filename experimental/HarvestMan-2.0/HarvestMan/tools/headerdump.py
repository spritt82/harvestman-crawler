#!/usr/bin/env python
# -- coding: latin-1

"""Dump the URL headers for
a project, from its cache. The
headers are dumped in the form
of a DBM file.

NOTE: This will work only if the cache file
has an entry for URL headers.

Author: Anand B Pillai <anand at harvestmanontheweb.com>

Copyright (C) 2005: Anand B Pillai

This file is part of HarvestMan package.
"""

import shelve
import os

def dump_headers(cacheobj, cachefilename):

    # Get name of project from cache filename.
    projname = (os.path.splitext(os.path.basename(cachefilename)))[0]
    dbmfile = ''.join((projname,'-headers.dbm'))
    shelf = shelve.open(dbmfile)
        
    for url,d in cacheobj.items():
        if d.has_key('headers'):
            entry = d['headers']
            if entry:
                shelf[url] = d['headers']

    shelf.close()
    print 'Wrote URL headers to %s.' % dbmfile

if __name__=="__main__":
    import sys

    if len(sys.argv)<2:
        sys.exit("Usage: %s <HarvestMan cache file>" % sys.argv[0])
        
    # Pick up modules from parent
    # directory.
    sys.path.append("..")
    from utils import HarvestManCacheManager
    from common import Initialize

    Initialize()
    try:
        cm=HarvestManCacheManager(sys.argv[1])
        dump_headers(cm.read_project_cache(), sys.argv[1])
    except OSError, e:
        print e
    except Exception, e:
        print e
        

