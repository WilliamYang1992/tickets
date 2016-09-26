# tickets
使用Python获取12306火车余票信息
Train tickets query via command line

# Characteristic
    1. 支持中文输入站点, 如"北京"
    2. 支持时间输入格式多样化, 如"今天"

# Usage:
    tickets.py [-gdtkz] [--lang=<en>] [--debug] <from> <to> <date>
    
# Options:
    -h --help 显示帮助菜单
    -g        高铁
    -d        动车
    -t        特快
    -k        快速
    -z        直达
    --lang:   选择语言, 可选cn或en
    --debug   开启debug信息
    
# Example:
    tickets.py shanghai beijing 2016-10-01
    tickets.py --lang en shanghai beijing 2016-10-01
    tickets.py 上海 北京 今天
    <form>, <to>: shanghai 上海 上hai BEIJING
    <date>: 2016-10-01 20161001 16-10-01 2016-10-1 jintian 今天
            mingtian 明天 houtian 后天
