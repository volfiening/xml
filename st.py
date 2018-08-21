import win32service
import win32serviceutil
import win32event
import win32evtlogutil
import win32traceutil
import servicemanager
import winerror
import logging
import inspect
import win32timezone
import win32trace
import time
import sys
import os
import re
import linecache
import xml.etree.ElementTree as et


class FixService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FixService"
    _svc_display_name_ = "FixService"
    _svc_description_ = "修复1014错误"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.isAlive = True
        
        self.case_log_dir = r'D:\YUM\OC\OrderCenterStoreService\CASE_Log'  # 路径
        self.current_time = time.strftime('%Y%m%d', time.localtime(time.time()))  # 当前时间
        self.case_log_file = os.path.join(self.case_log_dir, 'CASE_' + self.current_time + '.log')  # 文件

    def _getLogger(self):
        # logdir = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))#日志目录
        logger = logging.getLogger('fix logger')
        #handler = logging.FileHandler(filename=os.path.join(logdir,'Fix.log'))
        handler = logging.FileHandler(filename=r'd:\Fix.log',mode='w')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s-%(filename)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _getPos(self):
        if os.path.exists(self.case_log_file):
            tree = et.parse(r'd:\PosRequestResponseFramework_Config.xml')
            root = tree.getroot()
            pn = re.compile(r"/commcenter/[*]$")
            for item in root.iter('Route'):
                if pn.search(item.attrib['TopicFilter']):  # 读取下面的隐含pos机
                    # print(item.attrib['TopicFilter'])
                    for name in item.findall('Server'):  # 找到server下的pos机名
                        # print(name.attrib['Name'])
                        # print(self.case_log_file)
                        # pos.append(name.attrib['Name'])
                        if name.attrib['Priority'] == '1':  # 第一隐含pos
                            return name.attrib['Name']
    def _getLineCnt(self):
        if os.path.exists(self.case_log_file):
            linecache.clearcache()
            lines = linecache.getlines(self.case_log_file)
            return len(lines)

    def _CompareDateFile(self):
        nowtime = time.strftime('%Y-%m-%d',time.localtime(time.time()))

        with open(self.case_log_file) as f:
            for cnt,line in enumerate(f):
                start = line.find('|')#第一个|
                if cnt == 1:#随机取一行
                    filetime = line[start-19:start-9]
                    return filetime == nowtime

    def SvcStop(self):
        # tell Service Manager we are trying to stop (required)
        self.logger.info('service is end...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # write a message in the SM (optional)
        # import servicemanager
        # servicemanager.LogInfoMsg("FixService - Recieved stop signal")
        # set the event to call
        win32event.SetEvent(self.hWaitStop)
        self.isAlive = False

    def SvcDoRun(self):
        # import servicemanager
        # Write a 'started' event to the event log... (not required)
        #
        win32evtlogutil.ReportEvent(self._svc_name_, servicemanager.PYS_SERVICE_STARTED, 0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE, (self._svc_name_, ''))
        # methode 1: wait for beeing stopped ...
        # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        # methode 2: wait for beeing stopped ...
        self.timeout = 1000
        self.logger.info('service is begin...')

        cnt_end = 0#结束文件时行数

        while self.isAlive:
            # wait for service stop signal, if timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)

            self.logger.info('service is running...')
            if self._CompareDateFile():#当前时间和文件里时间一样
                cnt = self._getLineCnt()#初始行数
                self.logger.info('开始行数cnt'+str(cnt))

                if self._getLineCnt() and (cnt_end != cnt):#内容不为空
                #---------------------
                    for line in linecache.getlines(self.case_log_file):
                        start = line.find('|')#第一个|
                        end = line.find('|',line.find('|')+1)#第二个|
                        if line[start+1:end] == '1014':#发现错误
                            print(line[start-19:start])
                            #os.system('mstsc')
                            self.logger.info('执行mstsc')#重启pos机
                else:
                    self.logger.info('没新记录')

                cnt_end = self._getLineCnt()
                self.logger.info('最后行数cnt_end'+str(cnt_end))
                time.sleep(50)#间隔一分钟
            else:#当前时间和文件时间不一致，寻找当前时间的日志
                current_time = time.strftime('%Y%m%d',time.localtime(time.time()))#当前时间
                self.case_log_file = os.path.join(self.case_log_dir,'CASE_' + current_time + '.log')#文件
                cnt = self._getLineCnt()#初始行数
                cnt_end = 0#结束时文件行数

                if self._getLineCnt():#内容不为空
                #---------------------
                    for line in linecache.getlines(self.case_log_file):
                        start = line.find('|')#第一个|
                        end = line.find('|',line.find('|')+1)#第二个|
                        if line[start+1:end] == '1014':#发现错误
                            print(line[start-19:start])
                            #os.system('mstsc')
                            self.logger.info('执行mstsc')#重启pos机
                cnt_end = self._getLineCnt()#是否有新增行
                time.sleep(50)

            
            # ---------------------
            # and write a 'stopped' event to the event log (not required)
            #
        win32evtlogutil.ReportEvent(self._svc_name_, servicemanager.PYS_SERVICE_STOPPED, 0,servicemanager.EVENTLOG_INFORMATION_TYPE, (self._svc_name_, ''))
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
