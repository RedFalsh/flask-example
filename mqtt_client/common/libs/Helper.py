#!/usr/bin/env python
# encoding: utf-8


'''
获取当前时间
'''
def getCurrentDate( format = "%Y-%m-%d %H:%M:%S"):
    #return datetime.datetime.now().strftime( format )
    return datetime.datetime.now()

'''
获取格式化的时间
'''
def getFormatDate( date = None ,format = "%Y-%m-%d %H:%M:%S" ):
    if date is None:
        date = datetime.datetime.now()

    return date.strftime( format )

