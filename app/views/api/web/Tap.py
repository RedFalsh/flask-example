#!/usr/bin/env python
# encoding: utf-8

from app.views.api import route_api
from  flask import request,jsonify,g
import requests,json

from app import db
from app.model import User
from app.model import Member
from app.model import Device
from app.model import DeviceTap
from app.model import DeviceOperateLog
from app.model import DeviceOnlineLog
from app.model import DevicePowerLog
from app.model import DeviceTime

from app.common.libs.Logging import logger
from app.common.libs.UserService import UserService
from app.common.libs.DeviceService import DeviceService
from app.common.libs.Helper import getCurrentDate, getFormatDate

from sqlalchemy import desc


# 数据库修改方法
@route_api.route("/tap/sqldatainit",methods = [ "GET","POST" ])
def tapSqlDataInit():
    resp = { 'code':20000, 'message':'初始化成功', 'data':{}}
    device_list = Device.query.all()
    for device in device_list:
        tap1 = DeviceTap()
        tap1.device_id = device.id
        tap1.alias = device.alias1
        tap1.status = device.status1
        db.session.add(tap1)

        tap2 = DeviceTap()
        tap2.device_id = device.id
        tap2.alias = device.alias2
        tap2.status = device.status2
        db.session.add(tap2)
    db.session.commit()
    return jsonify( resp )


# 用户界面查询
@route_api.route("/tap/list",methods = [ "GET","POST" ])
def tapList():
    resp = { 'code':20000, 'message':'查询成功', 'data':{}}
    user_info = UserService.getUserInfo(request)
    req = request.values
    if user_info.roles == 'editor':
        resp = DeviceService.filterDeviceByEditor(req)
        return jsonify( resp )
    else:
        resp = DeviceService.filterDeviceByUser(req, user_info)
        return jsonify( resp )

    return jsonify( resp )

@route_api.route("/tap/edit",methods = [ "GET","POST" ])
def tapEdit():
    resp = { 'code':20000, 'message':'修改成功', 'data':{}}
    req = request.values
    sn = req['sn'] if 'sn' in req else ''
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['message'] = "need sn"
        return jsonify(resp)

    device_info = Device.query.filter_by( sn = sn ).first()
    if not device_info:
        resp['code'] = -1
        resp['message'] = '失败,设备不存在~'
        return jsonify(resp)

    position = req['position'] if 'position' in req else ''
    alias1 = req['alias1'] if 'alias1' in req else ''
    alias2 = req['alias2'] if 'alias2' in req else ''

    device_info.alias1 = alias1
    device_info.alias2 = alias2
    device_info.position = position

    db.session.commit()
    return jsonify(resp)

@route_api.route("/tap/info",methods = [ "GET","POST" ])
def tapInfo():
    resp = { 'code':20000, 'message':'查询成功', 'data':{}}
    req = request.values
    sn = req['sn'] if 'sn' in req else ''
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['message'] = "need sn"
        return jsonify(resp)

    resp = DeviceService.tapInfo(sn)

    return jsonify( resp )

@route_api.route("/tap/position/list",methods = [ "GET","POST" ])
def tapPositionList():
    resp = { 'code':20000, 'message':'修改成功', 'data':{}}
    req = request.values

    user_info = UserService.getUserInfo(request)
    positions = db.session.query(Device.position)\
        .filter(Member.id == Device.member_id )\
        .filter(User.mobile == Member.mobile )\
        .all()

    items = [p[0] for p in positions]
    items = list(set(items))

    resp['data']['items'] = items

    return jsonify(resp)

@route_api.route("/tap/operate/log/list",methods = [ "GET","POST" ])
def tapOperateLogList():
    resp = { 'code':20000, 'message':'查询成功', 'data':{}}
    req = request.values

    sn = req['sn'] if 'sn' in req else ''
    page = int( req['page'] ) if 'page' in req else 0
    limit = int( req['limit'] ) if 'limit' in req else 0
    offset = ( page - 1 ) * limit
    datetimeStart = req['datetimeStart'] if 'datetimeStart' in req else ''
    datetimeEnd = req['datetimeEnd'] if 'datetimeEnd' in req else ''


    user_info = UserService.getUserInfo(request)

    query = db.session.query(DeviceOperateLog, DeviceTap).filter( DeviceOperateLog.device_id == Device.id ).filter( Device.sn == sn )\
                                .filter( DeviceOperateLog.device_tap_id == DeviceTap.id)\
                                .filter( DeviceOperateLog.time.between(datetimeStart, datetimeEnd) )
    total = query.count()
    tap_log_list = query.order_by(desc(DeviceOperateLog.time)).offset( offset ).limit( limit ).all()

    items = []
    for log,tap in tap_log_list:
        items.append({
            'alias':  tap.alias,
            'msg':  log.msg,
            'time':  getFormatDate(log.time)
        })
    resp['data']['items'] = items
    resp['data']['total'] = total

    return jsonify( resp )


# 设备上下线记录
@route_api.route("/tap/online/log/list",methods = [ "GET","POST" ])
def tapOnlineLogList():
    resp = { 'code':20000, 'message':'查询成功', 'data':{}}
    req = request.values

    sn = req['sn'] if 'sn' in req else ''
    page = int( req['page'] ) if 'page' in req else 0
    limit = int( req['limit'] ) if 'limit' in req else 0
    offset = ( page - 1 ) * limit

    query = DeviceOnlineLog.query.filter( DeviceOnlineLog.device_id == Device.id ).filter( Device.sn == sn )
    total = query.count()
    log_list = query.order_by(desc(DeviceOnlineLog.time)).offset( offset ).limit( limit ).all()

    items = []
    for log in log_list:
        items.append({
            'online': log.online,
            'time': getFormatDate(log.time)
        })
    resp['data']['items'] = items
    resp['data']['total'] = total

    return jsonify( resp )

# 设备电量记录
@route_api.route("/tap/power/log/list",methods = [ "GET","POST" ])
def tapPowerLogList():
    resp = { 'code':20000, 'message':'查询成功', 'data':{}}
    req = request.values

    sn = req['sn'] if 'sn' in req else ''
    page = int( req['page'] ) if 'page' in req else 0
    limit = int( req['limit'] ) if 'limit' in req else 0
    offset = ( page - 1 ) * limit

    query = DevicePowerLog.query.filter( DevicePowerLog.device_id == Device.id ).filter( Device.sn == sn )
    total = query.count()
    log_list = query.order_by(desc(DevicePowerLog.time)).offset( offset ).limit( limit ).all()

    items = []
    for log in log_list:
        items.append({
            'power': str(log.power),
            'time': getFormatDate(log.time)
        })
    resp['data']['items'] = items
    resp['data']['total'] = total

    return jsonify( resp )

# 设备定时任务相关api
@route_api.route("/tap/clock/list",methods = [ "GET","POST" ])
def tapClockList():
    resp = {'code': 20000, 'message': 'ok~', 'data': {}}
    req = request.values

    sn = req['sn'] if 'sn' in req else ''
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['message'] = "need sn"
        return jsonify(resp)

    number = req['number'] if 'number' in req else 0
    if number == 0:
        resp['code'] = -1
        resp['message'] = "need number"
        return jsonify(resp)

    time_list = db.session.query(DeviceTime).\
                        filter(Device.sn==sn).\
                        filter(DeviceTime.device_id==Device.id).\
                        filter(DeviceTime.switch_num==number).\
                        all()
    items = []
    for d in time_list:
        items.append({
            'id':d.id,
            'type':d.type,
            'alive': d.alive,
            'period':d.period,
            'open_time':d.open_time,
            'number':d.switch_num,
            'close_time':d.close_time
        })

    resp['data']['items'] = items

    return jsonify(resp)

@route_api.route("/tap/clock/add",methods = [ "GET","POST" ])
def tapClockAdd():
    resp = {'code': 20000, 'message': '添加成功~', 'data': {}}
    req = request.values

    sn = req['sn'] if 'sn' in req else ''
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['message'] = "需要sn~"
        return jsonify(resp)

    device_info = Device.query.filter_by( sn = sn ).first()
    if not device_info:
        resp['code'] = -1
        resp['message'] = "当前设备不存在~~"
        return jsonify(resp)

    time_model = DeviceTime()

    _type = int(req['type']) if 'type' in req else 0
    open_time = req['open_time'] if 'open_time' in req else ''
    close_time = req['close_time'] if 'close_time' in req else ''
    number = int(req['number']) if 'number' in req else 0

    time_model.type = _type
    time_model.alive = 1
    time_model.device_id = device_info.id
    time_model.switch_num = number
    time_model.open_time = open_time
    time_model.close_time = close_time
    time_model.created_time = getCurrentDate()
    db.session.add(time_model)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/tap/clock/edit",methods = [ "GET","POST" ])
def tapClockEdit():
    resp = {'code': 20000, 'message': '修改成功~', 'data': {}}
    req = request.values

    id = int(req['id']) if 'id' in req else 0
    if id < 1:
        resp['code'] = -1
        resp['message'] = "need id"
        return jsonify(resp)

    time_info = DeviceTime.query.filter_by(id=id).first()

    _type = int(req['type']) if 'type' in req else 0
    open_time = req['open_time'] if 'open_time' in req else ''
    close_time = req['close_time'] if 'close_time' in req else ''

    time_info.type = _type
    time_info.open_time = open_time
    time_info.close_time = close_time
    time_info.updated_time = getCurrentDate()
    db.session.commit()

    return jsonify(resp)

@route_api.route("/tap/clock/delete",methods = [ "GET","POST" ])
def tapClockDelete():
    resp = {'code': 20000, 'message': '删除成功~', 'data': {}}
    req = request.values

    id = int(req['id']) if 'id' in req else 0
    if id < 1:
        resp['code'] = -1
        resp['message'] = "需要id"
        return jsonify(resp)

    DeviceTime.query.filter_by(id = id).delete()
    db.session.commit()

    return jsonify(resp)
