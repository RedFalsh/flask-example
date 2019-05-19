#!/usr/bin/env python
# encoding: utf-8

from app.views.api import route_api
from flask import request, jsonify, g
import json
import datetime

from app.common.libs.Helper import getCurrentDate

from app import db
from app.model import Member
from app.model import Device
from app.model import DeviceMqtt
from app.model import DeviceTime


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
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)

    name = req['name'] if 'name' in req else ''
    _type = req['type'] if 'type' in req else ''

    dev_info = Device.query.filter_by( sn = sn ).first()
    if dev_info:
        resp['code'] = -1
        resp['msg'] = "设备已存在"
        return jsonify( resp )

    # 添加设备
    model_device = Device()
    model_device.member_id = member_id
    model_device.sn = sn
    model_device.type = _type
    if _type == "tap":
        model_device.name = "阀门"
    else:
        model_device.name = name
    model_device.online = 0
    model_device.status = 0
    model_device.updated_time = model_device.created_time = getCurrentDate()
    db.session.add(model_device)
    db.session.commit()

    return jsonify( resp )

@route_api.route("/device/list",methods = [ "GET","POST" ])
def deviceList():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    auth_cookie = request.headers.get("Authorization")
    auth_info = auth_cookie.split("#")
    auth_id = auth_info[1]

    member_info = Member.query.filter_by( id = auth_id ).first()
    print(member_info)
    #  device_list = Device.query.filter_by( member_id = member_info.id ).first()
    device_list = db.session.query(Device).\
                        filter(Member.id==auth_id).\
                        filter(Member.id==Device.member_id).\
                        all()
    print(device_list)
    data = []
    for d in device_list:
        data.append({
            'name':d.name,
            'sn':d.sn,
            'type':d.type,
            'img':d.img,
            'position':d.position,
            'online':d.online,
            'status':d.status,
            'sub':'/dev/%s/sub'%d.sn,
            'pub':'/dev/%s/pub'%d.sn
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

    data = {
        'name':device_info.name,
        'sn':device_info.sn,
        'type':device_info.type,
        'img':device_info.img,
        'position':device_info.position,
        'online':device_info.online,
        'status':device_info.status,
        'sub':'/dev/%s/sub'%device_info.sn,
        'pub':'/dev/%s/pub'%device_info.sn
    }

    resp['data'] = data

    return jsonify(resp)

@route_api.route("/device/delete",methods = [ "GET","POST" ])
def deviceDelete():
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

    db.session.delete(device_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/device/time/add",methods = [ "GET","POST" ])
def deviceTimeAdd():
    resp = { 'code':200 ,'msg':'ok~','data':{} }

    req = request.values
    sn = req['sn'] if 'sn' in req else ''

    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)

    device_info = Device.query.filter_by( sn = sn ).first()
    if not device_info:
        resp['code'] = -1
        resp['msg'] = "device is not exist"
        return jsonify(resp)


    _type = req['type'] if 'type' in req else ''
    period = req['period'] if 'period' in req else ''
    open_time = req['open_time'] if 'open_time' in req else ''
    close_time = req['close_time'] if 'close_time' in req else ''

    # 添加定时任务
    model_time = DeviceTime()
    model_time.device_id = device_info.id
    model_time.alive = 1
    model_time.type = _type
    model_time.period = period
    model_time.open__time = open_time
    model_time.close__time = close_time
    model_time.updated_time = model_time.created_time = getCurrentDate()
    db.session.add(model_time)
    db.session.commit()

    return jsonify( resp )

@route_api.route("/device/time/edit",methods = [ "GET","POST" ])
def deviceTimeEdit():
    resp = { 'code':200 ,'msg':'ok~','data':{} }

    req = request.values
    sn = req['sn'] if 'sn' in req else ''

    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)

    id = req['id'] if 'id' in req else 0
    if id == 0:
        resp['code'] = -1
        resp['msg'] = "need id"
        return jsonify(resp)

    time_info = db.session.query(DeviceTime).\
                        filter(Device.sn==sn).\
                        filter(DeviceTime.device_id==Device.id).\
                        filter(DeviceTime.id==id).\
                        first()
    if not time_info:
        resp['code'] = -1
        resp['msg'] = "device time is not exist"
        return jsonify(resp)

    _type = req['type'] if 'type' in req else ''
    period = req['period'] if 'period' in req else ''
    open_time = req['open_time'] if 'open_time' in req else ''
    close_time = req['close_time'] if 'close_time' in req else ''

    # 添加定时任务
    time_info.alive = 1
    time_info.type = _type
    time_info.period = period
    time_info.open__time = open_time
    time_info.close__time = close_time
    time_info.updated_time = getCurrentDate()
    # db.session.update(time_info)
    db.session.commit()

    return jsonify( resp )

@route_api.route("/device/time/delete",methods = [ "GET","POST" ])
def deviceTimeDelete():
    resp = { 'code':200 ,'msg':'ok~','data':{} }

    req = request.values
    sn = req['sn'] if 'sn' in req else ''

    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)

    id = req['id'] if 'id' in req else 0
    if id == 0:
        resp['code'] = -1
        resp['msg'] = "need id"
        return jsonify(resp)

    time_info = db.session.query(DeviceTime).\
                        filter(Device.sn==sn).\
                        filter(DeviceTime.device_id==Device.id).\
                        filter(DeviceTime.id==id).\
                        first()
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

    sn = req['sn'] if 'sn' in req else ''
    if not sn or len( sn ) < 1:
        resp['code'] = -1
        resp['msg'] = "need sn"
        return jsonify(resp)

    time_list = db.session.query(DeviceTime).\
                        filter(Device.sn==sn).\
                        filter(DeviceTime.device_id==Device.id).\
                        all()
    print(time_list)
    data = []
    for d in time_list:
        data.append({
            'id':d.id,
            'type':d.type,
            'alive':d.alive,
            'period':d.period,
            'open_time':d.open__time,
            'close_time':d.close__time
        })

    resp['data'] = data

    return jsonify(resp)

