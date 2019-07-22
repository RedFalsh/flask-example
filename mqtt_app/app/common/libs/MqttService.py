#!/usr/bin/env python
# encoding: utf-8

import hashlib,requests,random,string,json
from app import  app

from app import db, mqtt
from app.model import Device
from app.model import DeviceTap
from app.model import DeviceOperateLog

from app.common.libs.Logging import logger
from app.common.libs.Helper import getCurrentDate, getFormatDate

import decimal

class MqttService():

    @staticmethod
    def getConnections( clientid ):
        """
        功能: 从mqtt服务器中获取客户端连接信息
        api: GET api/v3/connections/${clientid}
        """
        url = app.config['MQTT_SERVER_BASE_URLS'] + 'api/v3/connections/%s'%(clientid)
        r = requests.get(url, auth=(app.config['MQTT_SERVER_USER'],app.config['MQTT_SERVER_PASSWORD']))
        res = json.loads(r.text)
        if res['data']:
            return 1
        else:
            return 0
        return 0


    @staticmethod
    def getConnectionsByNode( clientid ):
        """
        功能: 从mqtt服务器中通过节点服务器获取客户端连接信息
        api: GET api/v3/${nodes}/connections/${clientid}
        """
        url = app.config['MQTT_SERVER_BASE_URLS'] + 'api/v3/nodes/%s/connections/%s'%(app.config['MQTT_SERVER_NODE'], clientid)
        r = requests.get(url, auth=(app.config['MQTT_SERVER_USER'],app.config['MQTT_SERVER_PASSWORD']))
        res = json.loads(r.text)
        return res


    @staticmethod
    def deviceOnline(sn):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( sn=sn ).first()
            print(device_info)
            if device_info:
                device_info.online = 1
                db.session.commit()
                return True

    @staticmethod
    def deviceOffline(sn):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                device_info.online = 0
                db.session.commit()
                return True

    @staticmethod
    def deviceChangedPower(sn, power):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                if power:
                    device_info.power = decimal.Decimal( float(power) )
                    db.session.commit()

    @staticmethod
    def deviceUpdateInfo(sn, info):
        with app.app_context():
            device_info = Device.query.filter_by( sn=sn ).first()
            if device_info:
                taps = DeviceTap.query.filter( DeviceTap.device_id == device_info.id).all()
                for key, value in info.items():
                    if key == "pow":
                        device_info.power = decimal.Decimal(float('%.2f'%value))
                    if key.startswith("sta"):
                        number = int(key[3:])
                        for tap in taps:
                            if tap.number == number:
                                tap.status = int(value)
                                break
                db.session.commit()
                return True

    @staticmethod
    def tapChangedStatus(sn, number, status):
        with app.app_context():
            device_info = Device.query.filter_by( sn = sn ).first()
            tap_info = DeviceTap.query.filter( DeviceTap.device_id == device_info.id)\
                                    .filter( DeviceTap.number == number).first()
            if tap_info:
                # 1号阀门状态
                tap_info.status = int(status)

                operate_log = DeviceOperateLog()
                operate_log.device_id = device_info.id
                operate_log.device_tap_id = tap_info.id
                operate_log.operate = int(status)
                operate_log.time = getCurrentDate()
                db.session.add(operate_log)

                db.session.commit()
                return True

    @staticmethod
    def deviceGetSn():
        with app.app_context():
            device_info = db.session.query(Device).filter_by( id=device_id ).first()
            return device_info.sn

    @staticmethod
    def deviceControlTap(time, cmd):
        with app.app_context():
            device_info = Device.query.filter_by( id=time.device_id ).first()
            tap_info = DeviceTap.query.filter_by( id=time.device_tap_id ).first()
            if device_info and tap_info:
                if device_info.online == 1:
                    sn = device_info.sn
                    number = tap_info.number
                    mqtt.publish('tap/%s/sw%s'%(sn,number), cmd, 0)
                    return True

    @staticmethod
    def deviceTapOpen(num, device_id):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( id=device_id ).first()
            if device_info:
                if device_info.online == 1:
                    sn = device_info.sn
                    if num == 1:
                        mqtt.publish('/tap/%s/sw1'%sn, "ON", 2)
                    if num == 2:
                        mqtt.publish('/tap/%s/sw2'%sn, "ON", 2)
                    return True

    @staticmethod
    def deviceTapClose(num, device_id):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( id=device_id ).first()
            if device_info:
                if device_info.online == 1:
                    sn = device_info.sn
                    if num == 1:
                        mqtt.publish('/tap/%s/sw1'%sn, "OFF", 2)
                    if num == 2:
                        mqtt.publish('/tap/%s/sw2'%sn, "OFF", 2)
                    return True



