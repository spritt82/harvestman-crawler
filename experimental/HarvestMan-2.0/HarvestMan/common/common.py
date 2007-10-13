# -- coding: latin-1
""" common.py - Global functions for HarvestMan Program.
    This file is part of the HarvestMan software.
    For licensing information, see file LICENSE.TXT.

    Author: Anand B Pillai <anand at harvestmanontheweb.com>

    Created: Jun 10 2003

    Aug 17 2006          Anand          Modifications for the new logging
                                        module.

    Feb 7 2007           Anand          Some changes. Added logconsole
                                        function. Split Initialize() to
                                        InitConfig() and InitLogger().
    Feb 26 2007          Anand          Replaced urlmappings dictionary
                                        with a WeakValueDictionary.

   Copyright (C) 2004 - Anand B Pillai.

"""

__version__ = '2.0 b1'
__author__ = 'Anand B Pillai'

import weakref
import os, sys
import socket
import binascii
import copy
import threading
import shelve
import threading

from types import *

class MyShelf(shelve.DbfilenameShelf):

    def __init__(self, filename, flag='c', protocol=None, writeback=False):
        shelve.DbfilenameShelf.__init__(self, filename, flag, protocol, writeback)
        self.cond = threading.Condition(threading.Lock())
            
    def get(self, key, default = None):
        try:
            return shelve.DbfilenameShelf.get(self, key, default)
        except AttributeError, e:
            pass
        except ValueError, e:
            pass

    def __setitem__(self, key, value):
        try:
            self.cond.acquire()
            shelve.DbfilenameShelf.__setitem__(self, key, value)
        finally:
            self.cond.release()
            
class CaselessDict(dict):
    
    def __setitem__(self, name, value):

        if type(name) in StringTypes:
            super(CaselessDict, self).__setitem__(name.lower(), value)
        else:
            super(CaselessDict, self).__setitem__(name, value)

    def __getitem__(self, name):
        if type(name) in StringTypes:
            return super(CaselessDict, self).__getitem__(name.lower())
        else:
            return super(CaselessDict, self).__getitem__(name)

    def __copy__(self):
        pass
            
class Registry(object):

    class __registrySingleton(object):

        def __init__(self):
            self.ini = 0
            self.writeflag = 1
            self.USER_AGENT = 'HarvestMan 2.0'
            self.userdebug = []
            self.modfilename = ''
            self.oldnewmappings = {}
            self.mappings = { 'HarvestManStateObject' : 'config',
                              'HarvestManNetworkConnector' : 'connector',
                              'HarvestManUrlConnectorFactory' : 'connectorfactory',
                              'HarvestManDataManager' : 'datamanager',
                              'HarvestManRulesChecker' : 'ruleschecker',
                              'HarvestManCrawlerQueue' : 'trackerqueue',
                              'HarvestMan' : 'crawler',
                              'HarvestManLogger'    : 'logger',
                              }
            pass
        
        def __str__(self):
            return `self`

        def get_object_key(self, obj):
            """ Return the object key for HarvestMan objects """

            clsname = obj.__class__.__name__
            return self.mappings.get(clsname, '')

        def get_class_key(self, classname):
            """ Return the object key for HarvestMan classes """

            return self.mapping.get(classname)
        
            
    instance = None

    def __new__(cls): # __new__ always a classmethod
        if not Registry.instance:
            Registry.instance = Registry.__registrySingleton()
            
        return Registry.instance

    def __getattr__(self, name):
        try:
            return getattr(self.instance, name)
        except KeyError:
            raise

    def __setattr__(self, name, value):
        setattr(self.instance, name, value)


if sys.version_info[0]==2 and sys.version_info[1]>=4:
    import collections

    class MyDeque(collections.deque):

        def index(self, item):
            """ Return the index of an item from the deque """

            return list(self).index(item)
            
        def insert(self, idx, item):
            """ Insert an item to the deque at the given index """
            
            myl = len(self)

            if myl==0:
                self.append(item)
                return
            elif idx==myl:
                self.append(item)
            elif idx>myl:
                raise IndexError, 'Index out of range'

            self.append(self.__getitem__(myl-1))
            for index in reversed(range(idx,myl)):
                self.__setitem__(index+1,self.__getitem__(index))

            self.__setitem__(idx, item)

        def pop(self, idx=None):
            """ Pop an item from the deque from the given index """

            # To be compatible with list
            myl = len(self)
            if idx==None:
                idx = myl - 1
            
            item = self.__getitem__(idx)
            # delete it
            self.__delitem__(idx)
            return item

        def remove(self, item):
            """ Remove an item from the deque """
            
            idx = self.index(item)
            self.__delitem__(idx)
else:
    MyDeque = list

# Single instance of the global lookup object
RegisterObj = Registry()

def SetMappings(mappings):

    global RegisterObj
    RegisterObj.mappings = mappings
    
def SysExceptHook(typ, val, tracebak):
    """ Dummy function to replace sys.excepthook """

    pass

def GetObject(objkey):
    """ Get the registered instance of the HarvestMan program
    object using its key <objkey> by looking up the global
    registry object """

    try:
        obj = eval('RegisterObj.' + str(objkey), globals())
        if type(obj)=='instance':
            return weakref.proxy(obj)
        else:
            return obj
    except (KeyError, AttributeError), e:
        pass

    return None   

def ResetState():

    from config import HarvestManStateObject
    
    global RegisterObj
    # Reset config object
    cfg = HarvestManStateObject()
    RegisterObj.config = cfg
    # Do not reset logger yet
    
def SetObject(obj):
    """ Set the instance <value> of the HarvestMan program object in
    the global registry object """

    # global RegisterObj
    # Get the object key
    objkey = RegisterObj.get_object_key(obj)

    if objkey:
        s="".join(('RegisterObj', '.', str(objkey),'=', 'obj'))
        exec(compile(s,'','exec'))

def SetLogFile():

    global RegisterObj
    
    logfile = RegisterObj.config.logfile
    # if logfile: RegisterObj.logger.setLogFile(logfile)
    if logfile:
        RegisterObj.logger.setLogSeverity(RegisterObj.config.verbosity)
        # If simulation is turned off, add file-handle
        if not RegisterObj.config.simulate:
            RegisterObj.logger.addLogHandler('FileHandler',logfile)

def SetUserAgent(user_agent):
    """ Set the user agent """

    global RegisterObj
    RegisterObj.USER_AGENT = user_agent

def SetUserDebug(message):
    """ Used to store error messages related
    to user settings in the config file/project file.
    These will be printed at the end of the program """

    global RegisterObj
    if message:
        try:
            RegisterObj.userdebug.index(message)
        except:
            RegisterObj.userdebug.append(message)

def InitConfig(configklass):
    """ Initialize the config object """

    global RegisterObj
    RegisterObj.config = configklass()
    return RegisterObj.config

def InitLogger(loggerklass):

    global RegisterObj
    RegisterObj.logger = loggerklass()
    return RegisterObj.logger

def SetLogSeverity():
    global RegisterObj
    RegisterObj.logger.setLogSeverity(RegisterObj.config.verbosity)    
    
def wasOrWere(val):
    """ What it says """

    if val > 1: return 'were'
    else: return 'was'

def plural((s, val)):
    """ What it says """

    if val>1:
        if s[len(s)-1] == 'y':
            return s[:len(s)-1]+'ies'
        else: return s + 's'
    else:
        return s

# file type identification functions
# this is the precursor of a more generic file identificator
# based on the '/etc/magic' file on unices.

signatures = { "gif" : [0, ("GIF87a", "GIF89a")],
               "jpeg" :[6, ("JFIF",)],
               "bmp" : [0, ("BM6",)]
             }
aliases = { "gif" : (),                       # common extension aliases
            "jpeg" : ("jpg", "jpe", "jfif"),
            "bmp" : ("dib",) }

def bin_crypt(data):
    """ Encryption using binascii and obfuscation """

    if data=='':
        return ''

    try:
        return binascii.hexlify(obfuscate(data))
    except TypeError, e:
        debug('Error in encrypting data: <',data,'>', e)
        return data
    except ValueError, e:
        debug('Error in encrypting data: <',data,'>', e)
        return data

def bin_decrypt(data):
    """ Decrypttion using binascii and deobfuscation """

    if data=='':
        return ''

    try:
        return unobfuscate(binascii.unhexlify(data))
    except TypeError, e:
        logconsole('Error in decrypting data: <',data,'>', e)
        return data
    except ValueError, e:
        logconsole('Error in decrypting data: <',data,'>', e)
        return data


def obfuscate(data):
    """ Obfuscate a string using repeated xor """

    out = ""
    import operator

    e0=chr(operator.xor(ord(data[0]), ord(data[1])))
    out = "".join((out, e0))

    x=1
    eprev=e0
    for x in range(1, len(data)):
        ax=ord(data[x])
        ex=chr(operator.xor(ax, ord(eprev)))
        out = "".join((out,ex))
        eprev = ex

    return out

def unobfuscate(data):
    """ Unobfuscate a xor obfuscated string """

    out = ""
    x=len(data) - 1

    import operator

    while x>1:
        apos=data[x]
        aprevpos=data[x-1]
        epos=chr(operator.xor(ord(apos), ord(aprevpos)))
        out = "".join((out, epos))
        x -= 1

    out=str(reduce(lambda x, y: y + x, out))
    e2, a2 = data[1], data[0]
    a1=chr(operator.xor(ord(a2), ord(e2)))
    a1 = "".join((a1, out))
    out = a1
    e1,a1=out[0], data[0]
    a0=chr(operator.xor(ord(a1), ord(e1)))
    a0 = "".join((a0, out))
    out = a0

    return out

def send_url(data, host, port):
    
    cfg = RegisterObj.config
    if cfg.urlserver_protocol == 'tcp':
        return send_url_tcp(data, host, port)
    elif cfg.urlserver_protocol == 'udp':
        return send_url_udp(data, host, port)
    
def send_url_tcp(data, host, port):
    """ Send url to url server """

    # Return's server response if connection
    # succeeded and null string if failed.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        sock.sendall(data)
        response = sock.recv(8192)
        sock.close()
        return response
    except socket.error, e:
        # print 'url server error:',e
        pass

    return ''

def send_url_udp(data, host, port):
    """ Send url to url server """

    # Return's server response if connection
    # succeeded and null string if failed.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data,0,(host, port))
        response, addr = sock.recvfrom(8192, 0)
        sock.close()
        return response
    except socket.error:
        pass

    return ''

def ping_urlserver(host, port):
    
    cfg = RegisterObj.config
    
    if cfg.urlserver_protocol == 'tcp':
        return ping_urlserver_tcp(host, port)
    elif cfg.urlserver_protocol == 'udp':
        return ping_urlserver_udp(host, port)
        
def ping_urlserver_tcp(host, port):
    """ Ping url server to see if it is alive """

    # Returns server's response if server is
    # alive & null string if server is not alive.
    try:
        debug('Pinging server at (%s:%d)' % (host, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        # Send a small packet
        sock.sendall("ping")
        response = sock.recv(8192)
        if response:
            debug('Url server is alive')
        sock.close()
        return response
    except socket.error:
        debug('Could not connect to (%s:%d)' % (host, port))
        return ''

def ping_urlserver_udp(host, port):
    """ Ping url server to see if it is alive """

    # Returns server's response if server is
    # alive & null string if server is not alive.
    try:
        debug('Pinging server at (%s:%d)' % (host, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Send a small packet
        sock.sendto("ping", 0, (host,port))
        response, addr = sock.recvfrom(8192,0)
        if response:
            debug('Url server is alive')
        sock.close()
        return response
    except socket.error:
        debug('Could not connect to (%s:%d)' % (host, port))
        return ''    

def GetTempDir():
    """ Return the temporary directory """

    # Currently used by hget
    tmpdir = max(map(lambda x: os.environ.get(x, ''), ['TEMP','TMP','TEMPDIR','TMPDIR']))

    if tmpdir=='':
        # No temp dir env variable
        if os.name == 'posix':
            if os.path.isdir('/tmp'):
                return '/tmp'
            elif os.path.isdir('/usr/tmp'):
                return '/usr/tmp'
        elif os.name == 'nt':
            profiledir = os.environ.get('USERPROFILE','')
            if profiledir:
                return os.path.join(profiledir,'Local Settings','Temp')
    else:
        return os.path.abspath(tmpdir)

def GetMyTempDir():
    """ Return temporary directory for HarvestMan """

    # This is tempdir/HarvestMan
    return os.path.join(GetTempDir(), 'harvestman')

# Modified to use the logger object
def info(arg, *args):
    """ Print basic information, will print if verbosity is >=1 """

    # Setting verbosity to 1 will print the basic
    # messages like project info and final download stats.
    RegisterObj.logger.info(arg, *args)

def moreinfo(arg, *args):
    """ Print more information, will print if verbosity is >=2 """

    # Setting verbosity to 2 will print the basic info
    # as well as detailed information regarding each downloaded link.
    RegisterObj.logger.moreinfo(arg, *args)    

def extrainfo(arg, *args):
    """ Print extra information, will print if verbosity is >=3 """

    # Setting verbosity to 3 will print more information on each link
    # as well as information of each thread downloading the link, as
    # well as some more extra information.
    RegisterObj.logger.extrainfo(arg, *args)    

def debug(arg, *args):
    """ Print debug information, will print if verbosity is >=4 """

    # Setting verbosity to 4 will print maximum information
    # plus extra debugging information.
    RegisterObj.logger.debug(arg, *args)    

def moredebug(arg, *args):
    """ Print more debug information, will print if verbosity is >=5 """

    # Setting verbosity to 5 will print maximum information
    # plus maximum debugging information.
    RegisterObj.logger.moredebug(arg, *args)        

def logconsole(arg, *args):
    """ Log directly to sys.stdout using print """

    # Setting verbosity to 5 will print maximum information
    # plus maximum debugging information.
    RegisterObj.logger.logconsole(arg, *args)        

if __name__=="__main__":
    InitConfig()
    cfg = GetObject('config')
    print type(cfg)
    
