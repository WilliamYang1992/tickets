#coding:utf-8

import re
import requests
from pprint import pprint

url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8966"

r = requests.get(url, params=None, verify = False)

stations_telecode_pinyin = re.findall(r'([A-Z]+)\|([a-z]+)', r.text)
stations_chinese_telecode = re.findall(r'([\u4e00-\u9fa5]{1,})\|([A-Z]{3})', r.text)

stations_telecode_pinyin = dict(stations_telecode_pinyin)
stations_pinyin_telecode = dict(zip(stations_telecode_pinyin.values(), stations_telecode_pinyin.keys()))

stations_chinese_telecode = dict(stations_chinese_telecode)
stations_telecode_chinese = dict(zip(stations_chinese_telecode.values(), stations_chinese_telecode.keys()))



print("stations_chinese_telecode = " , end='')
pprint(stations_chinese_telecode, indent= 4)
print("\n" * 10)
print("stations_telecode_chinese = ", end= '')
pprint(stations_telecode_chinese, indent= 4)
print("\n" * 10)
print("stations_pinyin_telecode = ", end= '')
pprint(stations_pinyin_telecode, indent= 4)
print("\n" * 10)
print("stations_telecode_pinyin = ", end= '')
pprint(stations_telecode_pinyin, indent= 4)

