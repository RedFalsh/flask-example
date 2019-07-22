#!/usr/bin/env python
# encoding: utf-8

"""
    项目配置文件config.py
"""

import os

DEBUG = False

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    # 打开跨站请求
    CSRF_ENABLED = True
    # SECRET_KEY = 'this-really-needs-to-be-changed'
    SECRET_KEY = 'Sm9obiBTY2hyb20ga2lja3MgYXNz'
    STRIPE_API_KEY = 'SmFjb2IgS2FwbGFuLU1vc3MgaXMgYSBoZXJv'

    MQTT_BROKER_URL = 'dqtttt.cn'
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = 'admin'
    MQTT_PASSWORD = 'public'
    MQTT_KEEPALIVE = 5
    MQTT_TLS_ENABLED = False

    MINA_APP = {
        'appid':'wx0c11db44a4804167',
        'appkey':'3c9d94cff87250d2e04f19e70ea95c9e',
        #  'appid':'wx544d45f6ce6ae390',
        #  'appkey':'3f87b3a3ba73d334995e575e0cc13295',
        'paykey':'xxxxxxxxxxxxxx换自己的',
        'mch_id':'xxxxxxxxxxxx换自己的',
        'callback_url':'/api/order/callback'
    }

    MQTT_SERVER_BASE_URLS = "http://dqtttt.cn:18083/"
    MQTT_SERVER_NODE = "emqx@127.0.0.1"
    MQTT_SERVER_USER = "admin"
    MQTT_SERVER_PASSWORD = "public"

    API_IGNORE_URLS = [
        "^/api"
    ]
    DEVICE_TIME_TYPE_MAPPING = {
        "0":"订单关闭",
        "1":"支付成功",
        "-8":"待支付",
        "-7":"待发货",
        "-6":"待确认",
        "-5":"待评价"
    }

class ProductionConfig(Config):
    DEBUG = False
    SERVER_PORT = 80
    #注意:  1、使用pymysql时需要mysql+pymysql才行!!!
    mysql = {
        'DATABASE': 'tap',
        'PASSWORD': 'p@ssw0rd123',
        'USER':     'root',
        'HOSTNAME': 'mysql', # docker用法
    }
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://%s:%s@%s/%s'%(mysql['USER'], mysql['PASSWORD'], mysql['HOSTNAME'], mysql['DATABASE'])
    #  SQLALCHEMY_ECHO = True
    #  SQLALCHEMY_TRACK_MODIFICATIONS = False
    #  SQLALCHEMY_ENCODING = "utf8mb4"


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SERVER_PORT = 5000
    mysql = {
        'DATABASE': 'tap',
        'PASSWORD': 'p@ssw0rd123',
        'USER':     'root',
        'HOSTNAME': 'dqtttt.cn:4000',
    }
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://%s:%s@%s/%s'%(mysql['USER'], mysql['PASSWORD'], mysql['HOSTNAME'], mysql['DATABASE'])
    #  SQLALCHEMY_ECHO = True
    #  SQLALCHEMY_TRACK_MODIFICATIONS = False
    #  SQLALCHEMY_ENCODING = "utf8mb4"

class TestingConfig(Config):
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
