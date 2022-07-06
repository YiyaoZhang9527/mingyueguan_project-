from tkinter.messagebox import NO
import pandas as pd
from subprocess import getoutput
from os.path import expanduser
from sys import path as sys_path
sys_path.append(expanduser("~/mingyueguan_project"))
from IPAddress_processing.query_geoip2 import PaserIPFromGeoIP2Batch
from IPAddress_processing.query_ipapi import batch_query

def transfrom_week(week):
    week_dict = {'Sun': '0',
            'Mon': '1',
            'Tue': '2',
            'Wed': '3',
            'Thu': '4',
            'Fri': '5',
            'Sat': '6'}
    if week in week_dict:
        return week_dict[week]
    else:
        return None
    
def tranfrom_month(month):
    month_dict = {'Jan': '01',
            'Feb': '02',
            'Mar': '03',
            'Apr': '04',
            'May': '05',
            'Jun': '06',
            'Jul': '07',
            'Aug': '08',
            'Sep': '09',
            'Oct': '10',
            'Nov': '11',
            'Dec': '12'}
    if month in month_dict:
        return month_dict[month]
    else:
        return None

def lastb_processing(lastb_getoutput):
    result_dict = {
        "用户名":[]
        ,"使用的登陆方式":[]
        ,"IP":[]
        ,"星期":[]
        ,"月份":[]
        ,"日期":[]
        ,"尝试登陆时间":[]
        ,"终止登陆时间":[]
        ,"持续时间":[]
    }


    for line in lastb_getoutput.splitlines():
        user,login_type,ip,week,month,day,start_time,end_time,keep_time = None,None,None,None,None,None,None,None,None
        token_line = line.split()
        if len(token_line) == 0:
            # print(0,token_line)
            pass
        elif len(token_line)==7:
            # print(7,token_line)
            pass
        elif len(token_line) == 9:
            #print(9,token_line)
            token_line.insert(0,None)
            user = token_line[0]
            login_type = token_line[1]
            ip = token_line[2]
            week = token_line[3]
            month = token_line[4]
            day = token_line[5]
            start_time = token_line[6]
            end_time = token_line[8]
            keep_time = token_line[9]
            pass
        elif len(token_line)==10:
            #print(token_line[0])
            user = token_line[0]
            login_type = token_line[1]
            ip = token_line[2]
            week = token_line[3]
            month = token_line[4]
            day = token_line[5]
            start_time = token_line[6]
            end_time = token_line[8]
            keep_time = token_line[9]
        else:
            pass
        #print(user,login_type,ip,week,month,day,start_time,end_time,keep_time)
        result_dict["用户名"].append(user)
        result_dict["使用的登陆方式"].append(login_type)
        result_dict["IP"].append(ip)
        result_dict["星期"].append(transfrom_week(week))
        result_dict["月份"].append(tranfrom_month(month))
        result_dict["日期"].append(day)
        result_dict["尝试登陆时间"].append(start_time)
        result_dict["终止登陆时间"].append(end_time)
        result_dict["持续时间"].append(keep_time)

    lastb_table = pd.DataFrame(result_dict)
    IPs= list(lastb_table.IP)
    print(set(IPs))
    IPinfo_table = PaserIPFromGeoIP2Batch(IPs)

    if IPinfo_table.size>0:
        lastb_table = pd.merge(lastb_table,IPinfo_table,on=["IP"])
    lastb_table.to_csv("lastb_table.csv")
    return lastb_table

if __name__ == '__main__':
        #显示所有列
    pd.set_option('display.max_columns', None)
    #显示所有行
    pd.set_option('display.max_rows', None)
    #设置value的显示长度为100，默认为50
    pd.set_option('max_colwidth',100)

    cmd = getoutput('ssh TencentServer5M "lastb -w"')
    lastb_table = lastb_processing(cmd)
    print(lastb_table)
    # IPinfo_table = PaserIPFromGeoIP2Batch(list(lastb_table.IP))
    # print(IPinfo_table.IP)
    # print(set(lastb_table.IP))

    
    
"""

"""