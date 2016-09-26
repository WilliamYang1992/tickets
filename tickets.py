#coding:utf-8
#Author: William Yang
#Version: V0.35dev


helpInfo = """
Train tickets query via command line

Usage:
    tickets.py [-gdctkz] [--lang=<en>] [--debug] <from> <to> <date>
    
Options:
    -h --help 显示帮助菜单
    -g        高铁
    -d        动车
    -c        城际
    -t        特快
    -k        快速
    -z        直达
    --lang:   选择语言, 可选cn或en
    --debug   开启debug信息
    
Example:
    tickets.py shanghai beijing 2016-10-01
    tickets.py --lang en shanghai beijing 2016-10-01
    tickets.py 上海 北京 今天
    <form>, <to>: shanghai 上海 上hai BEIJING
    <date>: 2016-10-01 20161001 16-10-01 2016-10-1 jintian 今天
            mingtian 明天 houtian 后天
"""


import os
import re
import sys
import requests
import xpinyin
from stations import *
from docopt import docopt
from pprint import pprint
from colorama import init
from xpinyin import Pinyin
from termcolor import colored
from formatdate import formatDate
from prettytable import PrettyTable
#导入该模块, 可以关闭不安全连接的警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def cli():
    """Command line interface"""
    global debug         #显示debug信息
    global detail        #显示返回的JSON信息
    global language      #语言选择
    
    transOpt = []        #保存转换后的参数
    typeOfTrainToDisplay = []    #保存需要显示的车次类型

    #显示帮助信息
    if len(sys.argv) == 2:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            os.system("cls")
            print(helpInfo)
            sys.exit()

    #获取命令行参数, 文本参数为"helpInfo", 并关闭默认帮助功能
    arguments = docopt(helpInfo, help= False)

    debug = arguments['--debug']
    language = arguments['--lang']
    from_station = stations_pinyin_telecode.get(chinese2pinyin(arguments['<from>']))
    to_station = stations_pinyin_telecode.get(chinese2pinyin(arguments['<to>']))
    date = formatDate(arguments['<date>'], "std")
    
    gaotie = arguments['-g']        #高铁选项
    dongche = arguments['-d']       #动车选项
    chengji = arguments['-c']         #城际选项
    tekuai = arguments['-t']        #特快选项
    kuaisu = arguments['-k']        #快速选项
    zhida = arguments['-z']         #直达选项
    
    #判断需要显示的列车类型, 传递到TrainCollection类进行筛选
    if gaotie == True:typeOfTrainToDisplay.append('G')
    if dongche == True:typeOfTrainToDisplay.append('D')
    if chengji == True:typeOfTrainToDisplay.append('C')
    if tekuai == True:typeOfTrainToDisplay.append('T')
    if kuaisu == True:typeOfTrainToDisplay.append('K')
    if zhida == True:typeOfTrainToDisplay.append('Z')
    
    
    transOpt.append(from_station)
    transOpt.append(to_station)
    transOpt.append(date)

    if not language is None:
        language = language.upper()
    else:
        language = "cn"

    if debug:
        print(arguments)
        print("from_station: {}".format(transOpt[0]))
        print("to_station: {}".format(transOpt[1]))
        print("date: {}".format(transOpt[2]))
    
    if language.upper() == "CN":
        print("\n查询中, 请耐心等待...")
    elif language.upper() == "EN":
        print("\nQuerying, please be patient...")


    #12306网站查询余票url
    url = "https://kyfw.12306.cn/otn/leftTicket/queryT?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(date, from_station, to_station)
    
    #取消不安全连接的警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    #发出查询请求, 返回JSON格式的车次信息
    r = requests.get(url, verify = False)
    
    try:
        rows = r.json()['data']
        #当detail为True时, 打印返回的JSON数据
        if detail:
            pprint(rows)
        trains = TrainCollection(rows, typeOfTrainToDisplay)
        if language.upper()  == "CN":
            print("\n日期: {}  出发地: {}  目的站: {}".format(date, stations_telecode_chinese.get(from_station),
                stations_telecode_chinese.get(to_station)))
        elif language.upper() == "EN":
            print("\nDate: {}  From station: {}  To station: {}".format(date,
                stations_telecode_pinyin.get(from_station), stations_telecode_pinyin.get(to_station)))
        #打印列车信息
        trains.pretty_print()        
    except(KeyError):
        if language.upper() == "CN":
            print("\n输入有误, 无法查询, 请重新更改条件后搜索\n")
        elif language.upper() == "EN":
            print("\nCan not query, please query agian with correct conditions\n")
    except(Exception) as e:
        if language.upper() == "CN":
            print("服务器出错, 无法查询\n"
                  "请稍后重新搜索\n")
        elif language.upper() == "EN":
            print("Server error, can not be queried\n"
                  "Please query again later")
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
    
    
    def __init__(self, rows, typeOfTrainToDisplay):
        self.rows = rows
        self.trains_num = self._get_train_count(self.rows)
        self.regexOfTrain = self._getTypeOfTrainToDisplay(typeOfTrainToDisplay)
        
        
    def _get_duration(self, row):
        """获取车次运行时间"""
        duration = row.get('lishi').replace(":", 'h') + 'm'
        
        #格式化"历时"时间格式
        if duration.startswith('00'):
            return duration[3:]
        if duration.startswith('0'):
            return '0' + duration[1:]
        return duration
    
    
    def _get_train_count(self, rows):
        """获取车次数量"""
        count = len(self.rows)
        return count
    
    
    def _getTypeOfTrainToDisplay(self, typeOfTrainToDisplay):
        temp = ""
        pattern = r"^[{}].*$"  #创建只含有需要显示的车次类型的正则表达式
        for i in typeOfTrainToDisplay:
            temp += i
        if not temp == "":
            return pattern.format(temp)
        else:
            #如果没有指定车次类型, 则返回可以匹配所有车次类型的正则表达式
            return pattern.replace("[{}]", "")
    
    
    @property
    def trains(self):
        index = 0  #记录循环中当前车次序号, 最后一列车次不加空行
        for row in self.rows:
            #列车信息在'queryLeftNewDTO'字典对应的值里面
            info = row['queryLeftNewDTO']
            #判断每一个车次是否在指定需要显示的车次类型列表内
            if re.match(self.regexOfTrain, info['station_train_code']):
                #如果'controlled_train_flag'不为0, 代表该车次因故停运
                if not info['controlled_train_flag'] == '0':
                    train = [
                        
                        colored(info['station_train_code'], 'white', 'on_red'),
                        
                        '\n'.join([colored(info['from_station_name'], 'red'), colored(info['to_station_name'], 'red')]),
                        
                        colored('-', 'red'),
                        
                        colored('-', 'red'),
                        
                        colored('-', 'red'),
                        
                        colored('-', 'red'),
                        
                        colored('-', 'red'),
                        
                        colored('-', 'red'),
                        
                        colored('-', 'red'),
                        
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
                        
                        colored('可预订', 'green'),
                        
                    ]
            else:
                #如果车次类型不在指定列表里, 则不显示
                continue
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
                      "please query again with proper condition\n")
        else:
            if language.upper() == "CN":
                print("\n共查询到 {} 车次, 详细信息如下:\n".format(self.trains_num))
                pt = PrettyTable(self.header_CN)
                for train in self.trains:
                    pt.add_row(train)
                print(pt)
            elif language.upper() == "EN":
                print("\nGet {} trains totally and the details as follow:\n".format(self.trains_num))
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
    init(autoreset= True)  #colorama初始化, 并设置自动还原
    if language.upper() == "CN":
        print("\n12306网站火车余票查询工具 Python专版 V0.35dev\n"
              "输入 -h 或 --help 获得帮助信息\n")
    elif language.upper() == "EN":
        print("\n12306 website TRAIN TICKET QUERY TOOL based on Python V0.35dev\n"
              "Enter -h or --help get helpful message\n")
    cli()
