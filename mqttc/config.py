#!/usr/bin/env python
# encoding: utf-8

import re

class config(object):

    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:#Redfalsh192729@localhost:3306/tap'

    MQTT_BROKER_URL = 'localhost'
    MQTT_BROKER_PORT = 1883
    MQTT_CLIENT_ID   = 'server_listen'
    MQTT_USERNAME = 'admin'
    MQTT_PASSWORD = 'public'
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = False

    MQTT_SUBCRIBE = [
        ("$SYS/brokers/emqx@127.0.0.1/clients/#", 0),
        ("/dev/#", 0),
    ]

    REGEX = {
        'connect': re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{10})/(connected|disconnected)'),
        'operate': re.compile(r'^/dev/([a-zA-Z0-9]{10})/(sub|pub)')
    }

    CMD = {
        'TAP_OPEN': 0xA1,
        'TAP_CLOSE': 0xA2,
        'TAP_STATUS': 0xA9,
        'TAP_ONLINE': 0xAA,
        'TAP_POWER': 0xB1,
        'TAP_SET_TIME':0xB2
    }

