#!/usr/bin/env python
#coding=utf-8
import xml.etree.ElementTree as et
import re,time,os,datetime,linecache

case_log_dir = r'D:\YUM\OC\OrderCenterStoreService\CASE_Log'#路径
current_time = time.strftime('%Y%m%d',time.localtime(time.time()))#当前时间
case_log_file = os.path.join(case_log_dir,'CASE_' + current_time + '.log')#文件
pos = list()#隐含pos
time_spliter = None#时间分隔

def readXML():

    case_log_dir = r'D:\YUM\OC\OrderCenterStoreService\CASE_Log'#路径
    current_time = time.strftime('%Y%m%d',time.localtime(time.time()))#当前时间
    case_log_file = os.path.join(case_log_dir,'CASE_' + current_time + '.log')#文件
    pos = list()#隐含pos
    time_spliter = None#时间分隔

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
        
        print(pos)

        #读取日志
        content = linecache.getlines(case_log_file)
        for line in content:
            start = line.find('|')#第一个|
            end = line.find('|',line.find('|')+1)#第二个|
            if line[start+1:end] == '1014':#发现错误
                print(line[start-19:start])


                
            
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
            
        
if __name__ == '__main__':
    readXML()