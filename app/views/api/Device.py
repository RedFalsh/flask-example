#!/usr/bin/env python
# encoding: utf-8

from app.views.api import route_api
from flask import request, jsonify, g
import json
import datetime

from app.common.libs.Helper import getCurrentDate
from app.common.libs.MqttService import MqttService
from app.common.libs.Logging import logger

from app import db
from app.model import Member
from app.model import Device
from app.model import DeviceTap
from app.model import DeviceTime
from app.model import DeviceOperateLog


# 设备相关api
@route_api.route("/device/add",methods = [ "GET","POST" ])
def deviceAdd():
    resp = { 'code':200 ,'msg':'ok~','data':{} }
    member_cookie = request.headers.get("Authorization")
    member_id = member_cookie.split("#")[1]
    if not member_id:
        resp['code'] = -1
        resp['msg'] = "need login"
        return jsonify(resp)

    req = request.values
    sn = req['sn'] if 'sn' in req else ''
    if not sn:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)

    number = req['number'] if 'number' in req else ''
    if not number:
        resp['code'] = -1
        resp['msg'] = "need number"
        return jsonify(resp)

    dev_info = Device.query.filter_by( sn = sn ).first()
    if dev_info:
        resp['code'] = -1
        resp['msg'] = "设备已存在"
        return jsonify( resp )

    # 添加设备
    model_device = Device()
    model_device.member_id = member_id
    model_device.sn       = sn
    model_device.number   = number
    model_device.name     = "智能阀门"
    model_device.position = '未设置'
    model_device.online   = 0
    model_device.status   = 0
    model_device.power    = 0
    model_device.updated_time = model_device.created_time = getCurrentDate()
    db.session.add(model_device)
    # 这里先提交，会生成一个设备id,后面添加子阀门用
    db.session.commit()

    # 添加设备子阀门
    if number == "dqt002":
        for i in range(2):
            model_tap = DeviceTap()
            model_tap.device_id = model_device.id
            model_tap.number = i+1
            model_tap.alias = "%s号阀门"%(i+1)
            model_tap.status = 0
            db.session.add(model_tap)
    db.session.commit()

    return jsonify( resp )

@route_api.route("/device/list",methods = [ "GET","POST" ])
def deviceList():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    auth_cookie = request.headers.get("Authorization")
    auth_info = auth_cookie.split("#")
    auth_id = auth_info[1]

    member_info = Member.query.filter_by( id = auth_id ).first()
    device_list = Device.query.\
                        filter(Member.id==auth_id).\
                        filter(Member.id==Device.member_id).\
                        all()
    data = []
    for d in device_list:
        # 从mqtt服务器中获取设备在线状态
        online = MqttService.getConnections(d.sn)
        d.online = online

        tap_list = DeviceTap.query.filter(DeviceTap.device_id == d.id).all()
        taps = [{
            'id' : tap.id,
            'alias' : tap.alias,
            'status' : tap.status,
            'number' : tap.number
        } for tap in tap_list]

        data.append({
            'id':d.id,
            'name':d.name,
            'sn':d.sn,
            'position':d.position,
            'online':d.online,
            'power':str(d.power),
            'taps': taps,
        })

    resp['data'] = data

    return jsonify(resp)

@route_api.route("/device/info",methods = [ "GET","POST" ])
def deviceInfo():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values

    sn = req['sn'] if 'sn' in req else ''
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)

    device_info = Device.query.filter_by( sn = sn ).first()
    if not device_info:
        resp['code'] = -1
        resp['msg'] = 'device not exist!'
        return jsonify(resp)

    device_info.online = MqttService.getConnections(device_info.sn)
    data = {
        'name':device_info.name,
        'sn':device_info.sn,
        'type':device_info.type,
        'img':device_info.img,
        'position':device_info.position,
        'online':device_info.online,
        'power':str(device_info.power),
        'status':device_info.status,
        'alias1':device_info.alias1,
        'status1':device_info.status1,
        'alias2':device_info.alias2,
        'status2':device_info.status2,
        'sub':'/dev/%s/sub'%device_info.sn,
        'pub':'/dev/%s/pub'%device_info.sn
    }

    resp['data'] = data

    return jsonify(resp)

@route_api.route("/device/delete/<string:sn>",methods = [ "GET","POST" ])
def deviceDelete(sn):
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    if not sn:
        resp['code'] = -1
        resp['msg'] = "需要设备编码"
        return jsonify(resp)

    device_info = Device.query.filter_by( sn = sn ).first()
    if not device_info:
        resp['code'] = -1
        resp['msg'] = '设备不存在'
        return jsonify(resp)

    db.session.delete(device_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/device/edit",methods = [ "GET","POST" ])
def deviceEdit():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values

    sn = req['sn'] if 'sn' in req else ''
    if not sn:
        resp['code'] = -1
        resp['msg'] = "失败,需要设备编码~"
        return jsonify(resp)

    device_info = Device.query.filter_by( sn = sn ).first()
    if not device_info:
        resp['code'] = -1
        resp['msg'] = '失败,设备不存在~'
        return jsonify(resp)

    # 更新设备信息
    name = req['name'] if 'name' in req else ''
    position = req['position'] if 'position' in req else ''
    device_info.name = name
    device_info.position = position

    #更新所属阀门信息
    taps = json.loads(req['taps']) if 'taps' in req else []
    for tap in taps:
        tap_info = DeviceTap.query.filter(DeviceTap.device_id == device_info.id).filter(DeviceTap.number == int(tap['number'])).first()
        if tap_info:
            tap_info.alias = tap['alias']

    db.session.commit()

    return jsonify(resp)

# 设备定时任务相关api
@route_api.route("/device/time/add",methods = [ "GET","POST" ])
def deviceTimeAdd():
    resp = { 'code':200 ,'msg':'ok~','data':{} }
    req = request.values

    tap_id = req['tap_id'] if 'tap_id' in req else 0
    if tap_id == 0:
        resp['code'] = -1
        resp['msg'] = "need tap_id"
        return jsonify(resp)

    _type = int(req['type']) if 'type' in req else 0
    alive = int(req['alive']) if 'alive' in req else 0
    period = req['period'] if 'period' in req else ''
    open_time = req['open_time'] if 'open_time' in req else ''
    close_time = req['close_time'] if 'close_time' in req else ''
    # 添加定时任务
    model_time = DeviceTime()
    model_time.device_tap_id = tap_id
    model_time.alive = alive
    model_time.type = _type
    model_time.period = period
    if _type == 1:
        model_time.open_flag = 0
        model_time.close_flag = 0
    model_time.open_time = open_time
    model_time.close_time = close_time
    model_time.updated_time = model_time.created_time = getCurrentDate()
    db.session.add(model_time)
    db.session.commit()

    return jsonify( resp )

@route_api.route("/device/time/edit",methods = [ "GET","POST" ])
def deviceTimeEdit():
    resp = { 'code':200 ,'msg':'ok~','data':{} }

    req = request.values

    time_id = req['time_id'] if 'time_id' in req else 0
    if time_id == 0:
        resp['code'] = -1
        resp['msg'] = "need time_id"
        return jsonify(resp)

    time_info = DeviceTime.query.filter_by(id = time_id).first()
    if not time_info:
        resp['code'] = -1
        resp['msg'] = "当前设备定时任务不存在,请刷新后再试~~"
        return jsonify(resp)

    _type = int(req['type']) if 'type' in req else 0
    alive = int(req['alive']) if 'alive' in req else 0
    period = req['period'] if 'period' in req else ''
    open_time = req['open_time'] if 'open_time' in req else ''
    close_time = req['close_time'] if 'close_time' in req else ''
    # 添加定时任务
    if alive:
        time_info.alive = alive
    # 类型：执行一次、每天、周末、工作日、自定义
    if _type:
        time_info.type = _type
        if _type == 1: # 执行一次的情况
            time_info.open_flag = 0
            time_info.close_flag = 0
    if period:
        time_info.period = period
    if open_time:
        time_info.open_time = open_time
    if close_time:
        time_info.close_time = close_time
    time_info.updated_time = getCurrentDate()
    # db.session.update(time_info)
    db.session.commit()

    return jsonify( resp )

@route_api.route("/device/time/delete",methods = [ "GET","POST" ])
def deviceTimeDelete():
    resp = { 'code':200 ,'msg':'ok~','data':{} }

    req = request.values
    time_id = req['time_id'] if 'time_id' in req else 0
    if time_id == 0:
        resp['code'] = -1
        resp['msg'] = "need time_id"
        return jsonify(resp)

    time_info = DeviceTime.query.filter_by(id = time_id).first()
    if not time_info:
        resp['code'] = -1
        resp['msg'] = "device time is not exist"
        return jsonify(resp)

    db.session.delete(time_info)
    db.session.commit()

    return jsonify( resp )

@route_api.route("/device/time/list",methods = [ "GET","POST" ])
def deviceTimeList():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values
    tap_id = req['tap_id'] if 'tap_id' in req else 0
    if tap_id == 0:
        resp['code'] = -1
        resp['msg'] = "need id"
        return jsonify(resp)

    time_list = db.session.query(DeviceTime).\
                        filter(DeviceTime.device_tap_id==DeviceTap.id).\
                        filter(DeviceTap.id==tap_id).\
                        all()
    data = []
    for d in time_list:
        data.append({
            'id':d.id,
            'type':d.type,
            'alive':d.alive,
            'period':d.period,
            'open_time':d.open_time,
            'close_time':d.close_time
        })

    resp['data'] = data

    return jsonify(resp)


# 设备操作日志api
@route_api.route("/device/operatelog/list",methods = [ "GET","POST" ])
def deviceOperateLogList():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values
    id = req['id'] if 'id' in req else 0
    if id == 0:
        resp['code'] = -1
        resp['msg'] = "need id"
        return jsonify(resp)
    log_list = db.session.query(DeviceOperateLog).\
                        filter(DeviceOperateLog.device_tap_id==DeviceTap.id).\
                        filter(DeviceTap.id == id).\
                        order_by(DeviceOperateLog.time.desc()).\
                        all()

    data = []
    for l in log_list:
        data.append({
            'msg':l.msg,
            'date':l.time.strftime("%Y-%m-%d"),
            'time':l.time.strftime("%H:%M"),
            'month':l.time.strftime("%m"),
            'day':l.time.strftime("%d"),
            'week':l.time.strftime("%w"),
        })
    resp['data'] = data

    return jsonify(resp)


# 设备连接状态获取api
@route_api.route("/device/connections",methods = [ "GET","POST" ])
def deviceConnections():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values
    sn_list = req['sn_list'] if 'sn_list' in req else []
    connections = {}
    if sn_list:
        sn_list = json.loads(sn_list)
        for sn in sn_list:
            connections[sn] = {'online': MqttService.getConnections(sn)}

    resp['data'] = connections

    return jsonify(resp)

@route_api.route("/device/connection",methods = [ "GET","POST" ])
def deviceConnection():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values
    sn = req['sn'] if 'sn' in req else ''
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)
    resp['msg'] = MqttService.getConnections(sn)
    return jsonify(resp)




