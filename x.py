#!/usr/bin/env python
#coding=utf-8
import xml.etree.ElementTree as et
import re,time,os,datetime,linecache,logging

case_log_dir = r'D:\YUM\OC\OrderCenterStoreService\CASE_Log'#路径
current_time = time.strftime('%Y%m%d',time.localtime(time.time()))#当前时间
case_log_file = os.path.join(case_log_dir,'CASE_' + current_time + '.log')#文件
pos = list()#隐含pos



def _getLogger():
        #logdir = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))#日志目录
        logger = logging.getLogger('fix logger')
        #handler = logging.FileHandler(filename=os.path.join(logdir,'Fix.log'))
        handler = logging.FileHandler(filename=r'd:\Fix.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s-%(filename)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger 

def _getPos(case_log_file): 
    if os.path.exists(case_log_file):
        tree = et.parse(r'd:\PosRequestResponseFramework_Config.xml')
        root = tree.getroot()
        pn = re.compile(r"/commcenter/[*]$")
        for item  in root.iter('Route'):
            if pn.search(item.attrib['TopicFilter']):#读取下面的隐含pos机
                #print(item.attrib['TopicFilter'])
                for name in item.findall('Server'):#找到server下的pos机名
                    # print(name.attrib['Name'])
                    # print(self.case_log_file)
                    # pos.append(name.attrib['Name'])
                    if name.attrib['Priority'] == '1':#第一隐含pos
                        return name.attrib['Name']

logger = _getLogger()
pos = _getPos(case_log_file)#隐含pos

def _getLineCnt(case_log_file):
    if os.path.exists(case_log_file):
        linecache.clearcache()
        lines = linecache.getlines(case_log_file)
        return len(lines)

def _CompareDateFile(case_log_file):
    nowtime = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    with open(case_log_file) as f:
        for cnt,line in enumerate(f):
            start = line.find('|')#第一个|
            if cnt == 1:#随机取一行
                filetime = line[start-19:start-9]
                return filetime == nowtime

def readXML():

    case_log_dir = r'D:\YUM\OC\OrderCenterStoreService\CASE_Log'#路径
    current_time = time.strftime('%Y%m%d',time.localtime(time.time()))#当前时间
    case_log_file = os.path.join(case_log_dir,'CASE_' + current_time + '.log')#文件
    pos = list()#隐含pos
    

    if os.path.exists(case_log_file):
        tree = et.parse('PosRequestResponseFramework_Config.xml')
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
                        pos.append(name.attrib['Name'])
        
        print(pos[0])

        #读取日志
        content = linecache.getlines(case_log_file)
        linecnt = len(content)
        print(linecnt)

        # with open(case_log_file,'r') as f:
        #     for cnt,line in enumerate(f):
        #         if cnt == 1:
        #             start = line.find('|')#第一个|
        #             end = line.find('|',line.find('|')+1)#第二个|
        #             print(line[start-19:start-8])
        #             nowtime = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        #             filetime = line[start-19:start-9]
        #             print(len(nowtime))
        #             print(len(filetime))
        #             print(nowtime == filetime)
        cnt_end = 0#结束文件时行数
            
    while True:


        if _CompareDateFile(case_log_file):#当前时间和文件里时间一样
            cnt = _getLineCnt(case_log_file)#初始行数
            logger.info(cnt)

            if _getLineCnt(case_log_file) and (cnt_end != cnt):#内容不为空
            #---------------------
                for line in linecache.getlines(case_log_file):
                    start = line.find('|')#第一个|
                    end = line.find('|',line.find('|')+1)#第二个|
                    if line[start+1:end] == '1014':#发现错误
                        print(line[start-19:start])
                        #os.system('mstsc')
                        logger.info('执行mstsc')#重启pos机
            else:
                logger.info('没新记录')

            
            cnt_end = _getLineCnt(case_log_file)
            logger.info(cnt_end)
            time.sleep(10)#间隔一分钟
        else:#当前时间和文件时间不一致，寻找当前时间的日志
            current_time = time.strftime('%Y%m%d',time.localtime(time.time()))#当前时间
            case_log_file = os.path.join(case_log_dir,'CASE_' + current_time + '.log')#文件
            cnt = _getLineCnt(case_log_file)#初始行数
            cnt_end = 0#结束时文件行数

            if _getLineCnt(case_log_file):#内容不为空
            #---------------------
                for line in linecache.getlines(case_log_file):
                    start = line.find('|')#第一个|
                    end = line.find('|',line.find('|')+1)#第二个|
                    if line[start+1:end] == '1014':#发现错误
                        print(line[start-19:start])
                        #os.system('mstsc')
                        logger.info('执行mstsc')#重启pos机
            time.sleep(6*60)
            # else:
            #     logger.info('没新记录')
                
            #     cnt_end = _getLineCnt(case_log_file)
            #     time.sleep(60)#间隔一分钟


                


                
            
                # print(time.mktime(time.strptime(line[start-19:start],'%Y-%m-%d %H:%M:%S')))
                # # filetime = time.mktime(time.strptime(line[start-19:start],'%Y-%m-%d %H:%M:%S'))
                # # #当前时间
                # # curtime = time.mktime(time.localtime(time.time()))
                # if line[start+1:end] == '1014':#发现错误
                #     if timeflag < time.mktime(time.strptime(line[start-19:start],'%Y-%m-%d %H:%M:%S')):

                #         #print(line[start-19:start])
                #         print(time.mktime(time.strptime(line[start-19:start],'%Y-%m-%d %H:%M:%S')))
                #         #设置时间
                #         timeflag = time.mktime(time.strptime(line[start-19:start],'%Y-%m-%d %H:%M:%S'))
                        
                #             #cmd = r'shutdown /r /t 0 /m \\' + pos[0]
                #             #os.system(cmd)
                #             #time.sleep(3)#暂停3分钟

def test():
    tree = et.parse(r'd:\PosRequestResponseFramework_Config.xml')
    root = tree.getroot()
    pn = re.compile(r"/commcenter/[*]$")
    for item  in root.iter('Route'):
        if pn.search(item.attrib['TopicFilter']):#读取下面的隐含pos机
            #print(item.attrib['TopicFilter'])
            for name in item.findall('Server'):#找到server下的pos机名
                # print(name.attrib['Name'])
                # print(self.case_log_file)
                # pos.append(name.attrib['Name'])
                if name.attrib['Priority'] == '1':#第一隐含pos
                    return name.attrib['Name']


if __name__ == '__main__':
    print(test())