#coding:utf-8
#Author: William Yang
#Version: V1.1


"""
Train tickets query via command line

Usage:
    tickets.py [-gdtkz] <from> <to> <date>
    
Options:
    -h --help 显示帮助菜单
    -g        高铁
    -d        动车
    -t        特快
    -k        快速
    -z        直达
    
Example: tickets.py shanghai beijing 2016-10-01
         tickets.py 上海 北京 今天
         <form>, <to>: shanghai 上海 上hai BEIJING
         <date>: 2016-10-01 20161001 16-10-01 2016-10-1 jintian 今天
"""

import os
import requests
from termcolor import colored
from docopt import docopt
from pprint import pprint
from colorama import init
from xpinyin import Pinyin
from stations import stations
from formatdate import formatDate
from prettytable import PrettyTable
#导入该模块, 可以关闭不安全连接的警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def cli():
    """Command line interface"""
    global debug         #显示debug信息
    global detail        #显示车次详细信息
    global language      #语言选择
    
    arguments = docopt(__doc__, help= True)
    if debug:
        print(arguments)
    from_station = stations.get(chinese2pinyin(arguments['<from>']))
    to_station = stations.get(chinese2pinyin(arguments['<to>']))
    date = formatDate(arguments['<date>'], "std")
    
       
    #12306网站查询余票url
    url = "https://kyfw.12306.cn/otn/leftTicket/queryT?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(date, from_station, to_station)
    
    #取消不安全连接的警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(url, verify = False)
    
    if language.upper() == "CN":
        print("查询中, 请耐心等待...")
    elif language.upper() == "EN":
        print("Querying, please be patient...")
    
    try:
        rows = r.json()['data']
        if debug and detail:
            pprint(rows)
        trains = TrainCollection(rows)
        if language == "CN":
            print("\n日期: {}  出发地: {}  目的站: {}".format(date, from_station, to_station))
        elif language == "EN":
            print("\nDate: {}  From station: {}  To station: {}")
        #打印列车信息
        trains.pretty_print()        
    except(KeyError):
        if language.upper() == "CN":
            print("\n输入有误, 无法查询, 请重新更改条件后搜索\n")
        elif language.upper() == "EN":
            print("\nCan not query, please query agian with correct conditions\n")
    except(Exception) as e:
        if language.upper() == "CN":
            print("服务器出错, 无法查询")
        elif language.upper() == "EN":
            print("Server error, can not be queried")
        if debug:
            print(e)
            

def chinese2pinyin(string):
    """汉子转为拼音字母"""
    global debug
    p = Pinyin()
    #先将输入转为小写
    pinyin = p.get_pinyin(string.lower(), "")
    if debug:        
        print("拼音: " + pinyin)
    return pinyin
    

class TrainCollection():
    header_EN = "train station time duration first second softsleep hardsleep hardsit remark".split()
    header_CN = "车次 站点 时间 历时 一等座 二等座 软卧 硬卧 硬座 备注".split()
    
    
    def __init__(self, rows):
        self.rows = rows
        self.trains_num = self._get_train_count(self.rows)
        
        
    def _get_duration(self, row):
        """获取车次运行时间"""
        duration = row.get('lishi').replace(":", 'h') + 'm'
        
        #格式化时间
        if duration.startswith('00'):
            return duration[3:]
        if duration.startswith('0'):
            return '0' + duration[1:]
        return duration
    
    
    def _get_train_count(self, rows):
        """获取车次数量"""
        count = len(self.rows)
        return count
    
    
    @property
    def trains(self):
        index = 0  #记录循环中当前车次序号, 最后一列车次不加空行
        for row in self.rows:
            #列车信息在'queryLeftNewDTO'字典对应的值里面
            info = row['queryLeftNewDTO']
            #如果'controlled_train_flag'不为0, 代表该车次因故停运
            if not info['controlled_train_flag'] == '0':
                train = [
                    
                    colored(info['station_train_code'], 'white', 'on_red'),
                    
                    '\n'.join([info['from_station_name'], info['to_station_name']]),
                    
                    '-', 
                    
                    '-',
                    
                    '-',
                    
                    '-',
                    
                    '-', 
                    
                    '-', 
                    
                    '-', 
                    
                   colored(info['controlled_train_message'], 'red'), 
                        
                ]
            else:
                train = [
                    
                    colored(info['station_train_code'], 'blue', 'on_green'),
                    
                    '\n'.join([colored(info['from_station_name'], 'green'), colored(info['to_station_name'], 'yellow')]),
                    
                    '\n'.join([colored(info['start_time'], 'green'), colored(info['arrive_time'], 'yellow')]),
                    
                    self._get_duration(info),
                    
                    info['zy_num'],
                    
                    info['ze_num'],
                    
                    info['rw_num'],
                    
                    info['yw_num'],
                    
                    info['yz_num'],
                    
                    '可预订', 
                    
                ]
            #为保持整齐与美观, 尾行不用加多余空位
            if not index == self.trains_num - 1:
                train[0] += '\n\n'
            #序号加1
            index += 1
                
            yield train
            
            
    def pretty_print(self):
        global language
        if self.trains_num == 0:
            if language.upper() == "CN":
                print("\n没有查询到符合条件的车次信息, 请重新设定条件查询\n")
            elif language.upper() == "EN":
                print("\nCan not find any train meet the specific conditions, "
                      "please query again with apposite condition\n")
        else:
            if language.upper() == "CN":
                print("\n共查询到 {} 车次, 详细信息如下:\n".format(self.trains_num))
                pt = PrettyTable(self.header_CN)
                for train in self.trains:
                    pt.add_row(train)
                print(pt)
            elif language.upper() == "EN":
                print("\nGet {} trains totally and the detail as follow:\n".format(self.trains_num))
                #设置表头
                pt = PrettyTable(self.header_EN)
                #添加车次信息到每行数据里
                for train in self.trains:
                    pt.add_row(train)
                print(pt)                
                


if __name__ == '__main__':
    debug = False
    detail = False
    language = "CN"
    init(autoreset= True)
    if language.upper() == "CN":
        print("12306网站火车余票查询工具 Python专版 V1.0\n")
    elif language.upper() == "EN":
        print("12306 website TRAIN TICKET QUERY TOOL based on Python V1.0\n")
    cli()
