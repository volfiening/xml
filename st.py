import win32service
import win32serviceutil
import win32event
import win32evtlogutil
import win32traceutil
import servicemanager
import winerror,logging,inspect,win32timezone,win32trace
import time
import sys
import os,re
import xml.etree.ElementTree as et

class FixService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FixService"
    _svc_display_name_ = "FixService"
    _svc_description_ = "修复1014错误"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop=win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.isAlive=True
        self.pos = self._getPos()#隐含pos

    def _getLogger(self):
        #logdir = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))#日志目录
        logger = logging.getLogger('fix logger')
        #handler = logging.FileHandler(filename=os.path.join(logdir,'Fix.log'))
        handler = logging.FileHandler(filename=r'c:\Fix.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s-%(filename)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger 

    def _getPos(self): 
        case_log_dir=r'D:\YUM\OC\OrderCenterStoreService\CASE_Log'#路径
        current_time = time.strftime('%Y%m%d',time.localtime(time.time()))#当前时间
        case_log_file = os.path.join(case_log_dir,'CASE_' + current_time + '.log')#文件
        if os.path.exists(case_log_file):
            tree = et.parse(r'c:\PosRequestResponseFramework_Config.xml')
            root = tree.getroot()
            pn = re.compile(r"/commcenter/[*]$")
            for item  in root.iter('Route'):
                if pn.search(item.attrib['TopicFilter']):#读取下面的隐含pos机
                    #print(item.attrib['TopicFilter'])
                    for name in item.findall('Server'):#找到server下的pos机名
                        # print(name.attrib['Name'])
                        # print(case_log_file)
                        # pos.append(name.attrib['Name'])
                        if name.attrib['Priority'] == '1':#第一隐含pos
                            return name.attrib['Name']

    def SvcStop(self):
        # tell Service Manager we are trying to stop (required)
        self.logger.info('service is end...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # write a message in the SM (optional)
        # import servicemanager
        # servicemanager.LogInfoMsg("FixService - Recieved stop signal")
        # set the event to call
        win32event.SetEvent(self.hWaitStop)
        self.isAlive=False

    def SvcDoRun(self):
        # import servicemanager
        # Write a 'started' event to the event log... (not required)
        #
        win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STARTED, 0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))
        # methode 1: wait for beeing stopped ...
        # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        # methode 2: wait for beeing stopped ...
        self.timeout=1000
        self.logger.info('service is begin...')

        while self.isAlive:
            # wait for service stop signal, if timeout, loop again
            rc=win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            
            #---------------------
            
            self.logger.info(self.pos)
            
            time.sleep(2)
            #---------------------
        # and write a 'stopped' event to the event log (not required)
        #
        win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STOPPED, 0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        return
if __name__ == '__main__':
    # if called without argvs, let's run !
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(FixService)
            servicemanager.Initialize('FixService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as details:
            if details.args[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(FixService)