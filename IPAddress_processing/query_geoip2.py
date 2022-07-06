import geoip2.database
from os.path import expanduser
from sys import path as sys_path
sys_path.append(expanduser("~/mingyueguan_project"))
from IPAddress_processing.const_IPAddress import city_ip_databases
import pandas as pd
from IPAddress_processing.IPAddreassTools import is_puvlic

def get_location_from_geoip2(ip,dataset_path_of_city=city_ip_databases):
    '''
    本地数据库ip信息查询
    '''
    return_error = {"ip地址":ip
            ,"国家":{None}
            ,"省份":{None}
            ,"城市":{None}
            ,"纬度":None
            ,"经度":None}
    try:
        reader = geoip2.database.Reader(dataset_path_of_city)
        ip_object = reader.city(ip)
        #print(ip_object)
        if ip_object == None:
            return return_error
        return  {"ip地址":ip_object.traits.ip_address
    ,"国家":ip_object.country.names
    ,"省份":ip_object.subdivisions.most_specific.names
    ,"城市":ip_object.city.names
    ,"纬度":ip_object.location.latitude
    ,"经度":ip_object.location.longitude}
    except Exception:
        return return_error
        
def change_language_logic(info):
    '''
    本地数据库ip信息查询的语言选择逻辑
    '''
    if 'zh-CN' in info:
        return info['zh-CN']
    elif 'en' in info:
        return info['en']
    elif 'es' in info:
        return info['es']
    elif 'fr' in info:
        return info['fr']
    elif 'de' in info:
        return info['de']
    elif 'ru' in info:
        return info['ru']
    elif 'ja' in info:
        return info['ja']
    elif 'pt-BR' in info:
        return info['pt-BR']
    else:
        return None
    
    
def parse_ip_location_from_geoip2(ip):
    '''
    本地数据库ip信息查询
    '''
    if is_puvlic(ip):
        ip_infos = get_location_from_geoip2(ip)
        ipv4 = ip_infos['ip地址']
        init_countries = change_language_logic(ip_infos['国家'])
        init_provinces = change_language_logic(ip_infos["省份"])
        init_city = change_language_logic(ip_infos["城市"])
        latitude = ip_infos['纬度']
        longitude = ip_infos['经度']
        return {"IPAddress":ipv4,"Countries":init_countries,"Provinces":init_provinces
        ,"City":init_city,"Latitude":latitude,"Longitude":longitude}
    else:
        return ValueError("IPAddress is not a public address")

def batch_query(IPs:iter,return_error=False):
    '''
    本地数据库ip信息查询
    '''
    # type_of_IPs = type(IPs)
    if isinstance(IPs,(dict,set)):
        distinct =  IPs
    else:
        distinct = set(IPs)
    result = {
        "IP":[]
        ,"国家":[]
        ,"省":[]
        ,"城市":[]
        ,"维度":[]
        ,"经度":[]
    }
    error_dict = {}
    for ip in distinct:
        try:
            parse = parse_ip_location_from_geoip2(ip)
            result['IP'].append(parse['IPAddress'])
            result['国家'].append(parse['Countries'])
            result['省'].append(parse['Provinces'])
            result['城市'].append(parse['City'])
            result['维度'].append(parse['Latitude'])
            result['经度'].append(parse['Longitude'])
        except Exception as e:
            error_dict.update({ip:e}) 
            
    return_tb = pd.DataFrame(result)
    if return_error:
        return return_tb,error_dict
    return return_tb

if __name__ == '__main__':
    import os
    import re
    case_path = os.path.expanduser('~/mingyueguan_project/IPAddress_processing/ipv4casefile.txt')
    case_file = [re.sub(r"^[\w\s]",'',line).strip('\n').replace("'",'').replace(",",'') for line in open(case_path, 'r').readlines()]
    print(batch_query(case_file))
    print("get_location_from_geoip2:",get_location_from_geoip2('103.176.57.21'))
    print("get_location_from_geoip2:",get_location_from_geoip2("109.74.204.123"))
