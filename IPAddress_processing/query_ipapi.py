from sympy import im
from tqdm import tqdm
import time
import requests
import pandas as pd
import json
import os

def token_ipv4_list(ip_list:iter,batch=100):
    """
    分割ipv4的课迭代数据，分成每100个一组
    """
    return_dict = {}
    n = 0
    t = 0
    for ipv4 in ip_list:
        
        if n > (batch-1):
            t += 1
            n = 0
        n += 1
        if t in return_dict:
            return_dict[t].append(ipv4)
        else:
            return_dict.update({t:[ipv4]})
    # print(n)

    return return_dict


def batch_requests(ipv4_list:list):
    """
    批量请求接口
    """
    url = 'http://ip-api.com/batch?'
    # 定义接收参数及语言，可不传
    param = {
        'fields':'status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,mobile,proxy,hosting,query'
        ,'lang': 'zh-CN'
    }


    response = requests.post(url=url, params=param, json=ipv4_list)
    
    result_text = response.text
    #print(return_text)
    return json.loads(result_text)



def conter_ipv4_list(ipv4s_list):
    counter_dict = {ipv4:0 for ipv4 in ipv4s_list}
    
    for ipv4 in ipv4s_list:
        counter_dict[ipv4]+=1
        
    return counter_dict

def distinct_ipv4_list(ip_list):
    '''
    对ip列表去重
    '''
    return list(set(ip_list))

def vaild_and_query_maximun100(ip_list:list):
    """
    去重并验证批量ip请求是否超过100，如未超过则开始请求
    """
    if isinstance(ip_list,list):
        pass
    else:
        return ValueError("param must a list ,plecae check you input code")
    
    #distinct_ips = distinct_ipv4_list(ip_list)
    
    max_lenght = len(ip_list)
    if max_lenght > 100:
        return ValueError("The maximum number of IP addresses that can be processed is 100 ,\
                          \nHTTP 422 Unprocessable Entity")
    
    #print(counter_dict) 
        # 多ip查询
    return batch_requests(ip_list)


def parse_batch_query(result_json,ipv4s_list):
    counter = conter_ipv4_list(ipv4s_list)
    '''
    解析从ip-api批量查询的返回值
    '''
    
    message_dict = {"status":[],"message":[],"query":[],"counter":[]}
    status_dict = {
        'query':[],"counter":[],'status':[],'continent':[]
        ,'continentCode':[],'country':[],'countryCode':[]
        ,'region':[],'regionName':[],'city':[]
        ,'district':[],'zip':[],'lat':[],'lon':[]
        ,'timezone':[],'offset':[],'currency':[]
        ,'isp':[],'org':[],'as':[],'asname':[]
        ,'mobile':[],'proxy':[],'hosting':[]
        

    }
    for line in result_json:
        #print(line)
         # 查询不到ip地址数据的返回处理
        if "message" in line:
            for key,value in line.items():
                if key == 'query':
                    # print("counter:\n",counter,"value:\n",value)
                    if value == None:
                        message_dict["counter"].append(counter[None])
                    message_dict["counter"].append(counter[value])  
                message_dict[key].append(value)
            
         # 查询到ip地址数据的返回处理
        elif 'status' in line:
            for key,value in line.items():
                if key == 'query':
                    status_dict["counter"].append(counter[value])          
                status_dict[key].append(value)  

    return status_dict,message_dict

def batch_ipapi(ipv4s_list,batch):
    """
    从ip-api批量查询ip地址信息
    """
    distinct_ipv4s = distinct_ipv4_list(ipv4s_list)
    token_ip_list= token_ipv4_list(distinct_ipv4s,batch)
    
    query_list = []
    step = 0
    batch_number = 0
    start_time = time.time()
    for batchNo,ipv4_list in tqdm(token_ip_list.items(),desc="{}{}{}{}".format("Batch query ipv4 addresses,step : ",str(step),"counter : ",batch_number)):

        batch_number = batchNo
        step += 1
        limit = (step % 15) == 0
        if limit:
            cut_time = step15_time-start_time
            if cut_time < 60:
                print("{}{}{}".format("The next round will have to wait ",str(60-cut_time)," seconds") )
                time.sleep(60-cut_time)
            start_time = time.time()
        step15_time=time.time()
        
        #TODO 请求主体程序    
        query_batch_maximum_100 = vaild_and_query_maximun100(ipv4_list)
        
        if isinstance(query_batch_maximum_100,list):
            query_list+=query_batch_maximum_100
        else:
            print(query_batch_maximum_100)
            
    status_dict,message_dict = parse_batch_query(query_list,ipv4s_list)
    
    return status_dict,message_dict

def batch_query(ipv4s_list,batch=100):
    """
    批量查询ipv4地址的信息，每分钟上限15次
    """
    status_dict,message_dict = batch_ipapi(ipv4s_list,batch)
    status_table = pd.DataFrame(status_dict)
    column_name_dict = {'status': '成功',
    'message': '失败',
    'continent': '大陆名称',
    'continentCode': '大陆代码',
    'country': '国家名称',
    'countryCode': '两个字母的国家代码ISO3166-1Alpha-2',
    'region': '地区/州短代码（FIPS或ISO）',
    'regionName': '地区/州',
    'city': '城市',
    'district': '区（城市的细分）',
    'zip': '邮政编码',
    'lat': '纬度',
    'lon': '经度',
    'timezone': '时区 (tz)',
    'offset': '时区 UTC DST 偏移量（以秒为单位）',
    'currency': '本国货币',
    'isp': '网络服务商（ISP 名称）',
    'org': '组织机构名称',
    'as': 'AS编号和组织',
    'asname': 'AS的名称',
    'mobile': '移动网络（蜂窝连接）',
    'proxy': '代理',
    'hosting': '托管',
    'query': 'IP'}
    status_table.rename(columns=column_name_dict,inplace=True)
    ipv4_table = pd.DataFrame({"IP":ipv4s_list})
    full_table = pd.merge(ipv4_table,status_table,on=["IP"])
    return {"query_table":full_table,"error_dict":message_dict}




if __name__ == '__main__':
        
    lastb_table_path = os.path.expanduser('~/mingyueguan_project/LinuxDate_processing/lastb_table.csv' )   
    ipv4s = list(pd.read_csv(lastb_table_path).IP)
    batch_query(ipv4s,20)
