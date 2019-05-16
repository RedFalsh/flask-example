#!/usr/bin/env python
# encoding: utf-8

from app.views.api import route_api
from flask import request, jsonify, g
import json

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

@route_api.route("/device/list")
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

