#!/usr/bin/env python
# -- coding: latin-1

# Utility to print a human readable version
# of HarvestMan project file.

# Author: Anand B Pillai <anand at harvestmanontheweb.com>

# Copyright (C) 2004 - 2005: Anand B Pillai

# This file is part of HarvestMan package.

import zlib
import sys

def uncompressproject(projectfile):
    return zlib.decompress(open(projectfile, 'rb').read())

if __name__=="__main__":
    if len(sys.argv)<2:
        sys.exit("Usage: projectreader.py <harvestman project file>")
        
    print uncompressproject(sys.argv[1])

