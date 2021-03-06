#coding:utf-8

"""
Author: WilliamYang
Email: 505741310@qq.com
Github: WilliamYang1992.github.com
Version: 0.2.3dev
"""

import re
from time import time
from datetime import date
from datetime import datetime

#mode:
#std            e.g. 2016-10-01
#no-spliter     e.g. 20161001
#no_century     e.g. 16-10-01
#no-century-spliter  e.g. 161001

mode = "std"
formatStr = ["%Y-%m-%d", "%Y%m%d", "%Y%m-%d", "%Y-%m%d",
             "%y-%m-%d", "%y%m%d", "%y%m-%d", "%y-%m%d", ]

todayDict = ["", "TODAY", "JINTIAN", "JINRI", "今天", "今日", ]
tomorrowDict = ["TOMORROW", "MINGTIAN", "MINGRI", "明天", "明日"]
theDayAfterTomorrowDict = ["THEDAYAFTERTOMORROW", "HOUTIAN", "HOURI", "后天", "后日"]

def formatDate(dateStr, formatMode = mode):
    pattern = "%Y-%m-%d"
    
    if dateStr.upper() in todayDict:
        return date.today()
    if dateStr.upper() in tomorrowDict:
        dateObject = date.fromtimestamp(time() + 86400)
        return dateObject
    if dateStr.upper() in theDayAfterTomorrowDict:
        dateObject = date.fromtimestamp(time() + 86400 * 2)
        return dateObject
    
    if re.match("^[12][09]\d{2}-\d{1,2}-\d{1,2}$", dateStr):
        pattern = formatStr[0]
    elif re.match("^[12][09]\d{2}\d{1,2}\d{1,2}$", dateStr):
        pattern = formatStr[1]
    elif re.match("^[12][09]\d{2}\d{1,2}-\d{1,2}$", dateStr):
        pattern = formatStr[2]
    elif re.match("^[12][09]\d{2}-\d{1,2}\d{1,2}$", dateStr):
        pattern = formatStr[3]
    elif  re.match("^[19]\d-\d{1,2}-\d{1,2}$", dateStr):
        pattern = formatStr[4]
    elif re.match("^[19]\d\d{1,2}\d{1,2}$", dateStr):
        pattern = formatStr[5]
    elif re.match("^[19]\d\d{1,2}-\d{1,2}$", dateStr):
        pattern = formatStr[6]
    elif re.match("^[19]\d-\d{1,2}\d{1,2}", dateStr):
        pattern = formatStr[7]
    else:
        pass
        
    try:
        if formatMode.upper() == "STD":
            dateObject = datetime.strptime(dateStr, pattern)
            dateformatted = dateObject.strftime("%Y-%m-%d")
        elif formatMode.upper() == "NO-SPLITER":
            dateObject = datetime.strptime(dateStr, pattern)
            dateformatted = dateObject.strftime("%Y%m%d")
        elif formatMode.upper() == "NO_CENTURY":
            dateObject = datetime.strptime(dateStr, pattern)
            dateformatted = dateObject.strftime("%y-%m-%d")
        elif formatMode.upper() == "NO_CENTURY_SPLITER":
            dateObject = datetime.strptime(dateStr, pattern)
            dateformatted = dateObject.strftime("%y%m%d")
    except(ValueError):
        raise ValueError("You have entered {} which is a wrong time!".format(dateStr))
    
    return dateformatted
