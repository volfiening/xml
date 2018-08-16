# -*- coding: UTF-8 -*-
# 从文件中读取数据
import xml.etree.ElementTree as ET
import os, time, sys, re

# 强制编码uft8
reload(sys)
sys.setdefaultencoding('utf8')

# 全局唯一标识
unique_id = 1
# restartpos的关键字
restartpos = "restartpos"
yuzhi = "3600"


# 遍历所有的节点
def walkData(root_node, level, result_list):
    global unique_id
    temp_list = [unique_id, level, root_node.tag, root_node.attrib]
    result_list.append(temp_list)
    unique_id += 1

    # 遍历每个子节点
    children_node = root_node.getchildren()
    if len(children_node) == 0:
        return
    for child in children_node:
        walkData(child, level + 1, result_list)
    return


def getXmlData(file_name):
    level = 1  # 节点的深度从1开始
    result_list = []
    root = ET.parse(file_name).getroot()
    walkData(root, level, result_list)

    return result_list

# 读取文件最后一行
def getCaseLog(file_name):
    # 如果文件读内容为空
    try:
        with open(file_name, 'r') as f:
            lines = f.readlines()  # 读取所有行
            last_line = lines[-1]
    except:
        last_line = file_name+"time文件为空|code文件为空|message文件为空"
    finally:
        return last_line

# 得到重启的信息
def getRestartLog(filename):
    f = open(filename)
    content = f.read()
    f.close()
    s = "\n".join(re.findall('.*' + restartpos + '.*', content)).split('\n')[-1].split("|")[0]
    return s

def wlog(outPutFilename,message):
    f = open(outPutFilename, 'w+')
    print >> f, message + "|" + Case_Log_Error_Time
    f.close()
    f = open(outPutHistoryFilename, 'a')
    print >> f, message + "|" + Case_Log_Error_Time
    f.close()

if __name__ == '__main__':
    # file_name = 'd:\\aaa.xml'
    # comprise配置文件路径
    rebootScript = r'D:\BatTool\script\service\reboot.bat'
    fixErrorCode = "1005"
    file_name = 'C:\\Documents and Settings\\All Users\\POSRR\\PosRequestResponseFramework_Config.xml'
    # robert 的oca Case路径
    case_log_time = time.strftime('%Y%m%d', time.localtime(time.time()))
    Case_Log_File_Name = "D:\\YUM\\OC\\OrderCenterStoreService\\CASE_Log\\CASE_"+ case_log_time +".log"
    # 日志打印的时间
    theTime1 = str(int(time.time()))
    theTime2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    theTime = theTime1+ '|' + theTime2
    # 给自愈工具读取的日志的植入路径，绝对路径
    outPutFilename = "D:\\yum\\recovery_log\\temp\\fix"+fixErrorCode+".log"
    # 文件执行历史记录路径
    outPutHistoryFilename = "D:\\YUM\\recovery_log\\history\\fix"+fixErrorCode+"."+ case_log_time +".log"
    # 重启pos机器日志
    outPutHistoryRebootFilename = "D:\\YUM\\recovery_log\\history\\fix"+fixErrorCode+"."+ case_log_time +"reboot.log"

    Case_Log_Error_Time = ""
    if os.path.exists(outPutHistoryFilename):
        lastRestartPosTime = getRestartLog(outPutHistoryFilename)
    else:
        lastRestartPosTime = theTime1
    # print lastRestartPosTime.isdigit()
    # print theTime1.isdigit()
    # print yuzhi.isdigit()



    # 如果日志得不到为数值型的时间，则直接赋值日志时间为当前时间，跳开重启
    # lastRestartPosTime = "a"
    # print "aa"+lastRestartPosTime+"aa"
    if lastRestartPosTime.strip()=='':
        lastRestartPosTime=0
    if not str(lastRestartPosTime).isdigit():
        lastRestartPosTime = theTime1
    if lastRestartPosTime < 0:
        lastRestartPosTime = theTime1


    chazhi = (int(theTime1) - int(lastRestartPosTime))
    # print chazhi,yuzhi
    if int(chazhi) > int(yuzhi):

        if os.path.exists(file_name):
            R = getXmlData(file_name)
            a = 0

            # 循环得到xml节点
            posName = ""
            for x in R:
                # print x
                if x[2] == "Route":
                    if x[3]["TopicFilter"] == "/compris/commcenter/*":
                        if a == 0:
                            a = x[1] + 1
                if a > 0 and x[1] == a:
                    if x[3]["Priority"] == "1":
                        posName = x[3]["Name"]
                        break
            # 拼接命令
            if posName == "":
                principal = theTime + "未成功解析到posName"
            else:
                runCommand = r'D:\BatTool\script\service\psshutdown.exe \\' + posName + ' -u posuser -p Compris2008TechNology -f -r -t 0
                # os.system('PsExec.exe \\"+posName+' -u posuser -p Compris2008TechNology c:\yumv7\shutdown.bat'')
                if os.path.exists(Case_Log_File_Name):
                    Case_Log = getCaseLog(Case_Log_File_Name)
                    FlagCase_Log = getCaseLog(outPutHistoryFilename)
                    # 得到日志返回错误代码，比如1005
                    Case_Log_Error_Code = Case_Log.split("|")[1]
                    # 得到文件内容时间
                    Case_Log_Error_Time = Case_Log.split("|")[0]
                    # print Case_Log_Error_Time
                    # 历史文件内容时间，作为重复执行的标志位
                    FlagCase_Log_Time = FlagCase_Log.split("|")[2]
                    # print "A"+FlagCase_Log_Time[0:30]+"A"
                    # print "b"+Case_Log_Error_Time[0:30]+"b"
                    FlagCase_Log_Time_temp1 = FlagCase_Log_Time[0:25]
                    Case_Log_Error_Time_temp1 = Case_Log_Error_Time[0:25]
                    if FlagCase_Log_Time_temp1 == Case_Log_Error_Time_temp1:
                        principal = theTime + "|历史记录文件时间:[" + FlagCase_Log_Time_temp1 \
                                    + ", CaseLog文件时间:[" + Case_Log_Error_Time_temp1 \
                                    + "], 时间相同，自愈不执行"
                        wlog(outPutFilename, principal)
                    else:
                        if Case_Log_Error_Code == fixErrorCode:
                            principal = theTime + "|检测到错误代码:"+ Case_Log_Error_Code +", " + restartpos + ",开始执行重启pos机[" + posName + "]命令:[ " + runCommand + " ] "
                            wlog(outPutFilename,principal)

                            f = open(rebootScript, 'w+')
                            print >> f, r'echo =====start===== >> ' + outPutHistoryRebootFilename + ' 2>&1 '
                            print >> f, r'echo %date% %time% >> ' + outPutHistoryRebootFilename + ' 2>&1 '
                            print >> f, runCommand + ' >> ' + outPutHistoryRebootFilename + ' 2>&1 '
                            print >> f, r'echo ===== end ===== >> ' + outPutHistoryRebootFilename + ' 2>&1 '
                            f.close()
                            # time.sleep(100)
                            os.system(rebootScript)

                        else:
                            principal = theTime + "|非[ " + fixErrorCode +" ], 自愈不执行, 当前错误代码:[ " + Case_Log_Error_Code + " ]"
                            wlog(outPutFilename, principal)
                else:
                    principal = theTime + "|[ " + Case_Log_File_Name + " ] 文件不存在"
                    wlog(outPutFilename, principal)

        else:
            principal = theTime + "|[ " + file_name+ " 文件不存在 ] "
            wlog(outPutFilename, principal)
    else:
        principal = theTime + "|[ 执行时间未到:当前时间:"+theTime1+", 最后重启时间:"+lastRestartPosTime+", 执行间隔:" + yuzhi + ", 差值:" + str(chazhi)
        wlog(outPutFilename, principal)

