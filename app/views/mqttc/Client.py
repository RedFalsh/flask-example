#!/usr/bin/env python
# encoding: utf-8

from app.views.mqttc import route_mqtt

from app import app, mqtt, db
from app.model import Device,DeviceTime,DeviceOperateLog
from app.common.libs.MqttService import CMD
from app.common.libs.Helper import getFormatDate, getCurrentDate
from app.common.libs.Logging import logger

import re
import json
import time, threading

# mqtt.subscribe(topic="$SYS/#", qos=0)
# mqtt.subscribe(topic="$SYS/brokers", qos=0)
mqtt.subscribe(topic="$SYS/brokers/emqx@127.0.0.1/clients/#", qos=0)
# 订阅终端设备的信息
mqtt.subscribe(topic="/dev/#", qos=0)

DEVICE_CONNECTED = re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{10})/(connected|disconnected)')
#  DEVICE_DISCONNECTED = re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{8})/disconnected')
DEVICE_CONTROL = re.compile(r'^/dev/([a-zA-Z0-9]{10})/(sub|pub)')

# 设备操作记录保存
def DeviceOperateLogAdd(sn, code, msg, source):
    with app.app_context():
        device_info = Device.query.filter_by( sn=sn ).first()
        if device_info:
            operate_log = DeviceOperateLog()
            operate_log.device_id = device_info.id
            operate_log.code = code
            operate_log.msg = msg
            operate_log.source = source
            operate_log.time = getCurrentDate()
            db.session.add(operate_log)
            db.session.commit()

def DeviceStatusChanged(sn, status):
    with app.app_context():
        device_info = Device.query.filter_by( sn=sn ).first()
        if device_info:
            device_info.status = status
            db.session.commit()

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic=message.topic
    payload=str(message.payload.decode())
    res = DEVICE_CONNECTED.match(topic)
    if res:
        sn = res.group(2)
        connect = res.group(3)
        resp = {'code':CMD.TAP_ONLINE}
        with app.app_context():
            device_info = Device.query.filter_by( sn=sn ).first()
            if device_info:
                if connect == "connected":
                    device_info.online = 1
                    resp['msg'] = 1
                if connect == "disconnected":
                    device_info.online = 0
                    resp['msg'] = 0
                db.session.commit()
                mqtt.publish('/dev/%s/pub'%sn, json.dumps(resp))
    res = DEVICE_CONTROL.match(topic)
    if res:
        sn = res.group(1)
        sub_pub = res.group(2)
        payload = json.loads(payload)

        code = int(payload['code']) if 'code' in payload else ''
        msg = payload['msg'] if 'msg' in payload else ''

        logger.info("设备操作记录:")
        if sub_pub == 'sub':
            logger.info("user->device: %s"%payload)
            DeviceOperateLogAdd(sn,code,msg,'sub')
        if sub_pub == 'pub':
            logger.info("device->user: %s"%payload)
            DeviceOperateLogAdd(sn,code,msg,'pub')

        # 监听到阀门状态变化
        if int(code) == CMD.TAP_STATUS:
            logger.info("阀门状态发生变化:%s"%msg)
            DeviceStatusChanged(sn, int(msg))


#  @mqtt.on_log()
#  def handle_logging(client, userdata, level, buf):
    #  print(level, buf)


# @route_mqtt.route("mqtt/nodes")
# def mqttNodes():
    # return 'mqtt nodes'


def timerTask():
    logger.info("开启定时任务......")
    resp = {}
    def ControlTap(id, cmd):
        device_info = Device.query.filter_by( id=id ).first()
        if device_info:
            if device_info.online == 1:
                resp['code'] = cmd
                sn = device_info.sn
                mqtt.publish('/dev/%s/sub'%sn, json.dumps(resp))
                return True
    while True:
        time.sleep(30)
        time_now = getFormatDate(format="%H:%M")
        time_week = getFormatDate(format="%w")
        with app.app_context():
            time_info = DeviceTime.query.filter_by( alive=1 ).all()
            for t in time_info:
                if t.type == 1: # 执行一次的任务
                    if t.open_time == time_now:
                        if t.open_flag == 0:
                            if ControlTap(t.device_id, CMD.TAP_OPEN):
                                t.open_flag = 1
                                db.session.commit()
                    if t.close_time == time_now:
                        if t.close_flag == 0:
                            if ControlTap(t.device_id, CMD.TAP_CLOSE):
                                t.close_flag = 1
                                db.session.commit()
                    if t.open_flag == 1 and t.close_flag == 1:
                        # 单次任务的执行步骤完成, 关闭任务
                        t.alive = 0
                        db.session.commit()
                else: # 其他周期性的任务，按星期来执行
                    period = str(t.period).split(',')
                    if time_week in period:
                        if t.open_time == time_now:
                            ControlTap(t.device_id, CMD.TAP_OPEN)
                        if t.close_time == time_now:
                            ControlTap(t.device_id, CMD.TAP_CLOSE)

time_thread = threading.Thread(target=timerTask)
time_thread.setDaemon(True)
time_thread.start()



