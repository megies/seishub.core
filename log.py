# -*- coding: utf-8 -*-

import os
import traceback

from twisted.python import log, logfile

from seishub.core import ERROR, WARN, INFO, DEBUG
from seishub.config import Option, IntOption


LOG_LEVELS = {'OFF': -1,
              'ERROR': ERROR,
              'WARN': WARN,
              'INFO': INFO,
              'DEBUG': DEBUG}


class ErrorLog(log.FileLogObserver):
    """
    Error log only for logging error messages.
    """
    
    def emit(self, eventDict):
        #skip access messages
        if not eventDict["isError"]:
            return
        log.FileLogObserver.emit(self, eventDict)


class Logger(object):
    """
    A log manager to handle all incoming log calls. 
    
    You still may use twisted.python.log.msg and twisted.python.log.err to 
    emit log messages.
    """
    
    Option('logging', 'error_log_file', 'error.log',
        """If `log_type` is `file`, this should be a the name of the file.""")
    
    Option('logging', 'log_level', 'DEBUG',
        """Level of verbosity in log.
        
        Should be one of (`ERROR`, `WARN`, `INFO`, `DEBUG`).""")
    IntOption('logging', 'log_size', 1024*1024,
        """File size in bytes that triggers the server to move old logs to a 
        separate file.""")
    
    def __init__(self, env):
        # init new log
        self.env = env
        self.start()
    
    def start(self):
        log_dir = os.path.join(self.env.config.path, 'logs')
        
        # Get log level and rotation size
        log_level = self.env.config.get('logging', 'log_level').upper()
        log_size = self.env.config.get('logging', 'log_size')
        self.log_level = LOG_LEVELS.get(log_level, ERROR)
        
        # Error log
        errlog_file = self.env.config.get('logging', 'error_log_file')
        self.errlog_handler = logfile.LogFile(errlog_file, log_dir, 
                                              rotateLength=log_size)
        self.errlog = ErrorLog(self.errlog_handler)
        self.errlog.start()
    
    def stop(self):
        for l in log.theLogPublisher:
            log.removeObserver(l)
    
    def _formatMessage(self, level, msg, showTraceback, color=False):
        msg = '%6s  %s' % (level+':', msg)
        #if color:
        #    msg = '\\x%db[2;31;31m%s\\x1b[0m' % (color, msg)
        log.msg(msg, isError=True)
        if showTraceback:
            log.msg(traceback.format_exc(), isError=True)
    
    def http(self, code, msg, showTraceback=False):
        if code < 400:
            self.debug(msg, showTraceback)
        elif code < 500:
            self.info(msg, showTraceback)
        else:
            self.error(msg, showTraceback)
    
    def error(self, msg, showTraceback=False):
        if self.log_level < ERROR:
            return
        self._formatMessage('ERROR', msg, showTraceback, color=2)
        
    def warn(self, msg, showTraceback=False):
        if self.log_level < WARN:
            return
        self._formatMessage('WARN', msg, showTraceback, color=1)
    
    def info(self, msg, showTraceback=False):
        if self.log_level < INFO:
            return
        self._formatMessage('INFO', msg, showTraceback)
    
    def debug(self, msg, showTraceback=False):
        if self.log_level < DEBUG:
            return
        self._formatMessage('DEBUG', msg, showTraceback)
