#!/usr/bin/env python
# encoding: utf-8

from app.views.mqtt import route_mqtt
from app import app, mqtt, db
from app.model import Device
from app.common.libs.MqttService import cmd

import re
import json

# mqtt.subscribe(topic="$SYS/#", qos=0)
# mqtt.subscribe(topic="$SYS/brokers", qos=0)
mqtt.subscribe(topic="$SYS/brokers/emqx@127.0.0.1/clients/#", qos=0)
# 订阅终端设备的信息
mqtt.subscribe(topic="/dev/#", qos=0)

DEVICE_CONNECTED = re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{10})/(connected|disconnected)')
#  DEVICE_DISCONNECTED = re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{8})/disconnected')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic=message.topic
    payload=str(message.payload.decode())
    if DEVICE_CONNECTED.match(topic):
        res = DEVICE_CONNECTED.match(topic)
        sn = res.group(2)
        connect = res.group(3)
        with app.app_context():
            device_info = Device.query.filter_by( sn=sn ).first()
            if device_info:
                resp = {}
                resp['code'] = cmd.TAP_ONLINE
                if connect == "connected":
                    device_info.online = 1
                    resp['msg'] = 1
                if connect == "disconnected":
                    device_info.online = 0
                    resp['msg'] = 0
                db.session.commit()
                mqtt.publish('/dev/%s/pub'%sn, json.dumps(resp))

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


@route_mqtt.route("mqtt/nodes")
def mqttNodes():
    return 'mqtt nodes'
