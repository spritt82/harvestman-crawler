#!/usr/bin/env python
# -- coding: iso8859-1

# Utility to obfuscate the network proxy settings
# for use by HarvestMan config file

# Author: Anand B Pillai <anand at harvestmanontheweb.com>

# Copyright (C) 2004 - 2005: Anand B Pillai

# This file is part of HarvestMan package.

import os,sys

class proxy_obfuscator:
    """ The proxy obfuscator class """

    def __init__(self):
        self._results = {}

    def string_query(self, query, strict=True, comment=""):
        """ Routine to make a query to the user and retrieve
        a string """

        res=''
        if not strict:
            res=raw_input(query)

        while res=='' and strict:
            res=raw_input(query)
            if not res:
                print 'Please enter a non-empty string!'

        if res==" ":
            # Abort signalled using <space> key
            # generate the config file
            print '<Space> key pressed! '
            sys.exit("Dialog Aborted")
            
        return res        
    
    def dialog(self):
        
        # Results dictionary
        results = {}

        print '***You can terminate this dialog by pressing'
        print 'the <space> key at any time***'
        print ''

        try:
            self._results['server'] = self.string_query("Enter the name/ip of the proxy server: ")
            self._results['username'] = self.string_query("The proxy username if any (press <Enter> to skip) : ", False)
            if self._results['username']:
                try:
                    import getpass
                    self._results['passwd'] = getpass.getpass('The proxy password if any (press <Enter> to skip) : ')
                except:
                    self._results['passwd'] = self.string_query("The proxy password if any (press <Enter> to skip) : ", False)
            self._results['port'] = self.string_query("The proxy port (press <Enter> to use default port 80): ", False)
        
            self.__obfuscate()
        except KeyboardInterrupt:
            print '\n***User abort***'
        
    def __obfuscate(self):
        """ Obfuscate proxy entries and print them out """

        print "Printing proxy variables... (Copy/Paste to config file)\n"

        # Server
        print 'network.proxyserver\t' + bin_crypt(self._results['server'])
        # Port
        if not self._results['port']: self._results['port'] = '80'
        
        print 'network.proxyport\t' + str(self._results['port'])

        # User name
        if self._results['username']:
            print 'network.proxyuser\t' + bin_crypt(self._results['username'])
            if self._results['passwd']:
                print 'network.proxypasswd\t' + bin_crypt(self._results['passwd'])

        
if __name__=="__main__":
        
    sys.path.append("..")
    from common import *

    print 'Warning: Use this utility only if you connect to Internet using a proxy server'
    obf = proxy_obfuscator()
    obf.dialog()
    
        
