#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time

import win32api
import win32event
import win32service,win32timezone,win32trace
import win32serviceutil
import servicemanager,logging


class MyService(win32serviceutil.ServiceFramework):

    _svc_name_ = "MyService"
    _svc_display_name_ = "My Service"
    _svc_description_ = "My Service"

    def __init__(self, args):
        self.logger = self._getLogger()
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.logger('start')
            self.start()
            self.logger('wait')
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            self.logger('done')
        except BaseException as e:
            self.logger('Exception : %s' % e)
            self.SvcStop()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.logger('stopping')
        self.stop()
        self.logger('stopped')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start(self):
        time.sleep(10000)

    def stop(self):
        pass


    def _getLogger(self):
        # logdir = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))#日志目录
        logger = logging.getLogger('fix logger')
        # handler = logging.FileHandler(filename=os.path.join(logdir,'Fix.log'))
        handler = logging.FileHandler(filename=r'c:\Fix.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s-%(filename)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def sleep(self, minute):
        win32api.Sleep((minute*1000), True)
 
if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)
