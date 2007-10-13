#!/usr/bin/env python
# -- coding: latin-1
"""Re-create the website on the disk
for a project, from its cache file.

NOTE: This will work only if the cache file
has an entry for the actual data for the urls
of the HarvestMan project.

Author: Anand B Pillai
Copyright (C) 2005: Anand B Pillai

This file is part of HarvestMan package.
"""

import os

def build_site(cacheobj):

    count=0
    for d in cacheobj.values():
        if d.has_key('data'):
            fileloc = d['location']
            data = d['data']
            try:
                # If directory does not exist
                # create it
                dname = os.path.dirname(fileloc)
                if not os.path.exists(dname):
                    os.makedirs(dname)
                    
                f=open(fileloc,'wb')
                f.write(data)
                count += 1
                print 'Re-generated file %s...' % fileloc
            except Exception, e:
                print e
                continue

    print 'Regenerated %d files from cache.' % count
                
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
        build_site(cm.read_project_cache())
    except OSError, e:
        print e
    except Exception, e:
        print e
    


    



