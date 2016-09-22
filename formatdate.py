#coding:utf-8

"""
Author: WilliamYang
Email: 505741310@qq.com
Github: WilliamYang1992.github.com
Version: 0.1dev
"""

import re
from datetime import date
from datetime import datetime

#mode:
#std            e.g. 2016-10-01
#no-spliter     e.g. 20161001

mode = "std"
formatStr = ["%Y-%m-%d", "%Y%m%d", "%Y%m-%d", "%Y-%m%d",
             "%y-%m-%d", "%y%m%d", "%y%m-%d", "%y-%m%d", ]

todayDict = ["", "TODAY", "JINTIAN", "JINRI", "今天", "今日", ]


def formatDate(dateStr, formatMode = mode):
    pattern = "%Y-%m-%d"
    
    if dateStr.upper() in todayDict:
        return date.today()
    
    if re.match("^\d\d\d\d-\d+-\d+$", dateStr):
        pattern = formatStr[0]
    elif re.match("^\d\d\d\d\d+\d+$", dateStr):
        pattern = formatStr[1]
    elif re.match("^\d\d\d\d\d+-\d+$", dateStr):
        pattern = formatStr[2]
    elif re.match("^\d\d\d\d-\d+\d+$", dateStr):
        pattern = formatStr[3]
    elif  re.match("^\d\d-\d+-\d+$", dateStr):
        pattern = formatStr[4]
    elif re.match("^\d\d\d+\d+$", dateStr):
        pattern = formatStr[5]
    elif re.match("^\d\d\d+-\d+$", dateStr):
        pattern = formatStr[6]
    elif re.match("^\d\d-\d+\d+$", dateStr):
        pattern = formatStr[7]
        
    try:
        if formatMode.upper() == "STD":
            dateObject = datetime.strptime(dateStr, pattern)
            dateformatted = date.strftime("%Y-%m-%d")
        elif formatMode.upper() == "NO-SPLITER":
            dateObject = datetime.strptime(dateStr, pattern)
            dateformatted = date.strftime("%Y%m%d")
    except(ValueError):
        raise ValueError("You have entered {} which is a wrong time!".format(dateStr))
    
    return dateformatted