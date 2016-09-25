#coding:utf-8

import re
import requests
from pprint import pprint

url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8966"

r = requests.get(url, params=None, verify = False)

stations_pinyin_telecode = re.findall(r'([A-Z]+)\|([a-z]+)', r.text)
stations_chinese_telecode = re.findall(r'([\u4e00-\u9fa5]{1,})\|([A-Z]{3})', r.text)

stations_pinyin_telecode = dict(stations_pinyin_telecode)
stations_pinyin_telecode = dict(zip(stations_pinyin_telecode.values(), stations_pinyin_telecode.keys()))

stations_chinese_telecode = dict(stations_chinese_telecode)

pprint(stations_pinyin_telecode, indent = 4)
pprint(stations_chinese_telecode, indent= 4)
