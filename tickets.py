#coding:utf-8

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

import colorama
import requests
from docopt import docopt
from pprint import pprint
from stations import stations
from prettytable import PrettyTable

def cli():
    """Command line interface"""
    arguments = docopt(__doc__)
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']
       
    url = "https://kyfw.12306.cn/otn/leftTicket/queryT?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(date, from_station, to_station)
    
    r = requests.get(url, verify = False)
    rows = r.json()['data']
    #pprint(rows)
    trains = TrainCollection(rows)
    trains.pretty_print()


class TrainCollection():
    header = "train station time duration first second softsleep hardsleep hardsit remark".split()
    
    
    def __init__(self, rows):
        self.rows = rows
        
        
    def _get_duration(self, row):
        """获取车次运行时间"""
        duration = row.get('lishi').replace(":", 'h') + 'm'
        
        if duration.startswith('00'):
            return duration[3:]
        if duration.startswith('0'):
            return duration[1:]
        return duration
    
    
    @property
    def trains(self):
        for row in self.rows:
            info = row['queryLeftNewDTO']
            if info['controlled_train_flag'] == '1':
                train = [
                    
                    info['station_train_code'] + '\n' * 2,
                    
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
                    
                    info['station_train_code'] + '\n' * 2,
                    
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
                
            yield train
            
            
    def pretty_print(self):
        pt = PrettyTable(self.header)
        for train in self.trains:
            pt.add_row(train)
            #pt.add_row(('-------- ' * 10).split())
        print(pt)

if __name__ == '__main__':
    cli()
