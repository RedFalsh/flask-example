#!/usr/bin/env python
# encoding: utf-8

import hashlib,requests,random,string,json
from app import  app

from app import db, mqtt
from app.model import Device
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
            device_info = db.session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                power = info["pow"] if 'pow' in info else -1
                status1 = info["sta1"] if 'sta1' in info else -1
                status2 = info["sta2"] if 'sta2' in info else -1
                if power and status1 and status2:
                    device_info.status1 = int(status1)
                    device_info.status2 = int(status2)
                    device_info.power = decimal.Decimal(float(power))
                    db.session.commit()
                    return True

    @staticmethod
    def deviceChangedStatus_1(sn, status):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                # 1号阀门状态
                device_info.status1 = int(status)
                if status < 3:
                    # 添加记录
                    operate_log = DeviceOperateLog()
                    operate_log.device_id = device_info.id
                    if status == 0:
                        operate_log.msg = "关闭"
                    if status == 1:
                        operate_log.msg = "开启"
                    if status == 2:
                        operate_log.msg = "半开"
                    operate_log.time = getCurrentDate()
                    db.session.add(operate_log)
                db.session.commit()
                return True

    @staticmethod
    def deviceChangedStatus_2(sn, status):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                # 1号阀门状态
                device_info.status2 = int(status)
                if status < 3:
                    # 添加记录
                    operate_log = DeviceOperateLog()
                    operate_log.device_id = device_info.id
                    if status == 0:
                        operate_log.msg = "关闭"
                    if status == 1:
                        operate_log.msg = "开启"
                    if status == 2:
                        operate_log.msg = "半开"
                    operate_log.time = getCurrentDate()
                    db.session.add(operate_log)
                db.session.commit()
                return True

    @staticmethod
    def deviceOperateLogAdd(sn, msg, source):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                operate_log = DeviceOperateLog()
                operate_log.device_id = device_info.id
                operate_log.msg = msg
                operate_log.source = source
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
    def deviceControlTap(num, device_id, cmd):
        with app.app_context():
            device_info = db.session.query(Device).filter_by( id=device_id ).first()
            if device_info:
                if device_info.online == 1:
                    sn = device_info.sn
                    if num == 1:
                        mqtt.publish('/tap/%s/sw1'%sn, cmd, 2)
                    if num == 2:
                        mqtt.publish('/tap/%s/sw2'%sn, cmd, 2)
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



