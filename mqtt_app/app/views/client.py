#!/usr/bin/env python
# encoding: utf-8


from flask import Blueprint, render_template
from app import app, db, mqtt

from app.model import Device
from app.model import DeviceTime
from app.model import DeviceOperateLog

from app.common.libs.Logging import logger
from app.common.libs.MqttService import MqttService
from app.common.libs.Helper import getCurrentDate, getFormatDate

import schedule,time,threading
import re
import json

client = Blueprint('client', __name__,
                 template_folder='templates',
                 static_folder='static')

@client.route('/')
def index():
    return 'Whelecome My Flask Client'


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(topic="$SYS/brokers/+/clients/#", qos=0)
    mqtt.subscribe(topic="tap/#", qos=0)
    app.config['MQTT_CONNECTED']= True

@mqtt.on_disconnect()
def handle_disconnect(client, userdata, rc):
    app.config['MQTT_CONNECTED']= False


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode('utf-8')

    logger.info("监听到到消息------>:")
    logger.info("topic:"+topic)
    logger.info("payload:"+payload)

    # 匹配设备上线
    connect_res = re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{10})/(connected|disconnected)').match(topic)
    if connect_res:
        sn = connect_res.group(2)
        connect = connect_res.group(3)
        if connect == "connected":
            mqtt.publish('tap/%s/online'%sn,1)
            MqttService.deviceOnline(sn)
        if connect == "disconnected":
            mqtt.publish('tap/%s/online'%sn,0)
            MqttService.deviceOffline(sn)

    # 匹配设备相关操作
    operate_res = re.compile(r'^tap/([a-zA-Z0-9]{10})/(pub|sub)/(.*)').match(topic)
    if operate_res:
        sn = operate_res.group(1)
        pub_sub = operate_res.group(2)
        tag = operate_res.group(3)
        if pub_sub == "pub":
            if tag == "info":
                MqttService.deviceUpdateInfo(sn, json.loads(payload))

            if tag == "pow":
                MqttService.deviceChangedPower(sn, float(payload))
                logger.info("电量采集:%s"%payload)

            if tag == "sta1":
                MqttService.deviceChangedStatus_1(sn, int(payload))
                logger.info("1号阀状态变化:%s"%payload)

            if tag == "sta2":
                MqttService.deviceChangedStatus_2(sn, int(payload))
                logger.info("2号阀状态变化:%s"%payload)

def timerCheckConnected():
    if not app.config['MQTT_CONNECTED']:
        logger.error("设备断线请求重连中....")
        mqtt.reconnect()
        # Wait to reconnect

def timerTask():
    while True:
        schedule.run_pending()
        time.sleep(1)

def timerTaskJob():
    def deviceControlTap(num, device_id, cmd):
        device_info = db.session.query(Device).filter_by( id=device_id ).first()
        if device_info:
            logger.info("1")
            print(device_info.online)
            if device_info.online == 1:
                logger.info("2")
                if num == 1:
                    logger.info("3")
                    mqtt.publish('tap/%s/sw1'%sn, cmd, 2)
                    logger.info("定时任务打开阀门")
                if num == 2:
                    mqtt.publish('tap/%s/sw2'%sn, cmd, 2)
                return True

    try:
        with app.app_context():
            logger.info("执行定时任务......")
            # 线程中使用db.session需要添加一个新的对象来进行执行
            time_now = getFormatDate(format="%H:%M")
            time_week = getFormatDate(format="%w")
            time_info = db.session.query(DeviceTime).filter_by( alive=1 ).all()
            for t in time_info:
                if t.type == 1: # 执行一次的任务
                    if t.open_time == time_now:
                        if t.open_flag == 0:
                            if MqttService.deviceControlTap(t.switch_num, t.device_id, 'ON'):
                                t.open_flag = 1
                                db.session.commit()
                    if t.close_time == time_now:
                        if t.close_flag == 0:
                            if MqttService.deviceControlTap(t.switch_num, t.device_id, 'OFF'):
                                t.close_flag = 1
                                db.session.commit()
                    if t.open_flag == 1 and t.close_flag == 1:
                        # 单次任务的执行步骤完成, 关闭任务
                        t.alive = 0
                        db.session.commit()
                else: # 其他周期性的任务，按星期来执行
                    period = str(t.period).split(',')
                    if time_week == '0':
                        time_week = '7'
                    if time_week in period:
                        if t.open_time == time_now:
                            MqttService.deviceControlTap(t.switch_num, t.device_id, 'ON')
                        if t.close_time == time_now:
                            MqttService.deviceControlTap(t.switch_num, t.device_id, 'OFF')
    except Exception as e:
        logger.error(e)

time_thread = threading.Thread(target=timerTask)
time_thread.setDaemon(True)
time_thread.start()

schedule.every(20).seconds.do(timerTaskJob)
# schedule.every(3).seconds.do(timerCheckConnected)


