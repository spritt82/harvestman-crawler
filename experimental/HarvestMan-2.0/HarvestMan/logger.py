#! /usr/bin/env python

"""
logger.py -  Logging functions for HarvestMan.
This module is part of the HarvestMan program.

Author: Anand B Pillai <anand at harvestmanontheweb.com>

Created: Jan 23 2005

Modification History

   Aug 17 06 Anand   Made this to use Python logging module.

Copyright (C) 2005 Anand B Pillai.

"""

__version__ = '2.0 b1'
__author__ = 'Anand B Pillai'

import logging, logging.handlers
import os, sys

class HandlerFactory(object):
    """ Factory class to create handlers of different families for use by SIMLogger """
    
    def createHandle(handlertype, *args):
        """ Return a logging handler of the given type.
        The handler will be initialized using params from the args
        argument tuple """

        if handlertype == 'StreamHandler':
            return logging.StreamHandler(*args)
        elif handlertype == 'FileHandler':
            return logging.FileHandler(*args)
        elif handlertype == 'SocketHandler':
            return logging.handlers.SocketHandler(*args)        
        
    createHandle = staticmethod(createHandle)

        
class HarvestManLogger(object):
    """ A customizable logging class for HarvestMan with different
    levels of logging support """

    # Useful macros for setting
    # the log level.
    
    DISABLE = 0
    INFO = 1
    MOREINFO  = 2
    EXTRAINFO = 3
    DEBUG   = 4
    MOREDEBUG = 5

    # Dictionary from levels to level names
    _namemap = { 0: 'DISABLE',
                 1: 'INFO',
                 2: 'MOREINFO',
                 3: 'EXTRAINFO',
                 4: 'DEBUG',
                 5: 'MOREDEBUG' }

    # Map of instances
    _instances = {'default': None}
    
    def __init__(self, severity=1, logflag=2):
        """ Initialize the logger class with severity and logflag """
        
        self._severity = severity
        
        if logflag==0:
            self._severity = 0
        else:
            self._severity = severity
            if logflag == 2:
                self.consolelog = True
                
        self._logger = logging.Logger('HarvestMan')

        if self.consolelog:
            formatter = logging.Formatter('[%(asctime)s] %(message)s',
                                          '%H:%M:%S')
            handler = logging.StreamHandler()
            handler.setLevel(self._severity)
            
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        else:
            pass

    def _getMessage(self, arg, *args):
        """ Private method to create a message string from the supplied arguments """

        try:
            return ''.join((str(arg),' ',' '.join([str(item) for item in args])))
        except UnicodeEncodeError:
            return ''.join((str(arg),' ',' '.join([str(item.encode('iso-8859-1')) for item in args])))

    def getLevelName(self, level):
        """ Return the level name, given the level value """
        
        return self._namemap.get(level, '')

    def getLogLevel(self):
        """ Return the current log level """

        # Same as severity
        return self.getLogSeverity()

    def getLogSeverity(self):
        """ Return the current log severity """

        return self._severity

    def getLogLevelName(self):
        """ Return the name of the current log level """

        return self.getLevelName(self._severity)

    def setLogSeverity(self, severity):
        """ Set the log severity """

        self._severity = severity

    def addLogHandler(self, handlertype, *args):
        """ Generic method to add a handler to the logger """

        # handlertype should be a string
        # Call helper function here
        handler = HandlerFactory.createHandle(handlertype, *args)
        handler.setLevel(1)
        formatter = logging.Formatter('%(asctime)s %(message)s',
                                          '(%d-%m-%y) [%H:%M:%S]')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        
    def enableConsoleLogging(self):
        """ Enable console logging - if console logging is already
        enabled, this method does not have any effect """

        console = 'StreamHandler' in [h.__class__.__name__ for h in self._logger.handlers]
        
        if not console:
            formatter = logging.Formatter('[%(asctime)s] %(message)s',
                                          '%H:%M:%S')
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        else:
            pass

    def disableConsoleLogging(self):
        """ Disable console logging - if console logging is already
        disabled, this method does not have any effect """

        # Find out streamhandler if any
        for h in self._logger.handlers:
            if h.__class__.__name__ == 'StreamHandler':
                # Remove the handler
                self._logger.removeHandler(h)
                break
        else:
            pass

    def disableFileLogging(self):
        """ Disable file logging - if file logging is already
        disabled, this method does not have any effect """

        # Find out filehandler if any
        for h in self._logger.handlers:
            if h.__class__.__name__ == 'FileHandler':
                # Remove the handler
                self._logger.removeHandler(h)
                break
        else:
            pass

    def info(self, msg, *args):
        """ Perform logging at the INFO level """

        try:
            (self._severity>=1) and self._logger.debug(self._getMessage(msg, *args))
        except ValueError, e:
            pass
        except IOError, e:
            pass

    def moreinfo(self, msg, *args):
        """ Perform logging at the MOREINFO level """

        try:
            (self._severity>=2) and self._logger.debug(self._getMessage(msg, *args))
        except ValueError, e:
            pass
        except IOError, e:
            pass
        
    def extrainfo(self, msg, *args):
        """ Perform logging at the EXTRAINFO level """

        try:
            (self._severity>=3) and self._logger.debug(self._getMessage(msg, *args))
        except ValueError, e:
            pass
        except IOError, e:
            pass
        
    def debug(self, msg, *args):
        """ Perform logging at the DEBUG level """

        try:
            (self._severity>=4) and self._logger.debug(self._getMessage(msg, *args))
        except ValueError, e:
            pass
        except IOError, e:
            pass
        
    def moredebug(self, msg, *args):
        """ Perform logging at the MOREDEBUG level """

        try:
            (self._severity>=5) and self._logger.debug(self._getMessage(msg, *args))
        except ValueError, e:
            pass
        except IOError, e:
            pass
        
    def logconsole(self, msg, *args):
        """ Directly log to console using sys.stdout """

        try:
            (self._severity>0) and sys.stdout.write(self._getMessage(msg, *args)+'\n')
        except ValueError, e:
            pass
        except IOError, e:
            pass
        
    def getDefaultLogger(cls):
        """ Return the default logger instance """

        return cls._instances.get('default')
    
    def Instance(cls, name='default', *args):
        """ Return an instance of this class """

        inst = cls(*args)
        cls._instances[name] = inst

        return inst

    def shutdown(self):
        logging.shutdown()

    Instance = classmethod(Instance)
    getDefaultLogger = classmethod(getDefaultLogger)
    
if __name__=="__main__":
    import sys
    
    mylogger = HarvestManLogger.Instance()
    mylogger.addLogHandler('FileHandler','report.log')
    mylogger.setLogSeverity(2)
    
    p = 'Spikesource'
    mylogger.info("Test message 1",p)
    mylogger.moreinfo("Test message 2",p)
    mylogger.extrainfo("Test message 3",p)
    mylogger.debug("Test message 4",p)
    mylogger.moredebug("Test message 5",p)
    
    print mylogger.getLogSeverity()
    print mylogger.getLogLevelName()

    mylogger.enableConsoleLogging()
    # mylogger.disableConsoleLogging()    
    mylogger.disableFileLogging()
    
    mylogger.info("Test message 1",p)
    mylogger.moreinfo("Test message 2",p)
    mylogger.extrainfo("Test message 3",p)
    mylogger.debug("Test message 4",p)
    mylogger.moredebug("Test message 5",p)


    print HandlerFactory.createHandle('StreamHandler', sys.stdout)
    print HandlerFactory.createHandle('FileHandler', 'my.txt')
    print HandlerFactory.createHandle('SocketHandler', 'localhost', 5555)

    mylogger.info("Test message 1",p)
    mylogger.moreinfo("Test message 2",p)
    mylogger.extrainfo("Test message 3",p)
    mylogger.debug("Test message 4",p)
    mylogger.moredebug("Test message 5",p)    

    print HarvestManLogger.getDefaultLogger()==mylogger
    print HarvestManLogger._instances
