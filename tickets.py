#coding:utf-8
#Author: William Yang
#Version: V1.1


"""
Train tickets query via command line.

Usage:
    tickets [-gdtkz] <from> <to> <date>
    
Options:
    -h,--help 显示帮助菜单
    -g        高铁
    -d        动车
    -t        特快
    -k        快速
    -z        直达
"""

import os

import colorama
import requests
from docopt import docopt
from pprint import pprint
from xpinyin import Pinyin
from stations import stations
from prettytable import PrettyTable

def cli():
    """Command line interface"""
    global debug
    global language
    
    if language.upper() == "CN":
        print("查询中, 请耐心等待...")
    elif language.upper() == "EN":
        print("Querying, please be patient...")
    
    arguments = docopt(__doc__)
    if debug:
        print(arguments)
    from_station = stations.get(chinese2pinyin(arguments['<from>']))
    to_station = stations.get(chinese2pinyin(arguments['<to>']))
    date = arguments['<date>']
       
    url = "https://kyfw.12306.cn/otn/leftTicket/queryT?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(date, from_station, to_station)

    r = requests.get(url, verify = False)
    try:
        rows = r.json()['data']
        if debug:
            pprint(rows)
        trains = TrainCollection(rows)
        trains.pretty_print()        
    except(KeyError):
        print("\n你的输入有误, 无法查询, 请重新更改条件后搜索\n")
    except(Exception) as e:
        print("服务器出错, 无法查询")
        if debug:
            print(e)
            

def chinese2pinyin(string):
    global debug
    p = Pinyin()
    pinyin = p.get_pinyin(string, "")
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
        index = 0  #记录循环中当前车次序号
        for row in self.rows:
            #列车信息在'queryLeftNewDTO'字典对应的值里面
            info = row['queryLeftNewDTO']
            #如果'controlled_train_flag'不为0, 代表该车次因故停运
            if not info['controlled_train_flag'] == '0':
                train = [
                    
                    info['station_train_code'],
                    
                    '\n'.join([info['from_station_name'], info['to_station_name']]),
                    
                    '-', 
                    
                    '-',
                    
                    '-',
                    
                    '-',
                    
                    '-', 
                    
                    '-', 
                    
                    '-', 
                    
                    info['controlled_train_message'], 
                        
                ]
            else:
                train = [
                    
                    info['station_train_code'],
                    
                    '\n'.join([info['from_station_name'], info['to_station_name']]),
                    
                    '\n'.join([info['start_time'], info['arrive_time']]),
                    
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
            #序号加一
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
                pt = PrettyTable(self.header_EN)
                for train in self.trains:
                    pt.add_row(train)
                print(pt)                
                


if __name__ == '__main__':
    debug = True
    language = "CN"
    if language.upper() == "CN":
        print("TITLE 12306网站火车余票查询工具 Python专版 V1.0\n")
    elif language.upper() == "EN":
        print("TITLE 12306 website TRAIN TICKET QUERY TOOL based on Python V1.0\n")
    cli()
