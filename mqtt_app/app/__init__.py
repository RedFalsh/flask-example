#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mqtt import Mqtt
from config import config
import os

# app初始化,
# instance_relative_config 设置config文件可从Instance文件中查找
app = Flask(__name__, instance_relative_config=True)

# 配置文件导入
app.config.from_object(config['development'])

# 数据库管理
db = SQLAlchemy()
db.init_app(app)

# mqtt初始化
mqtt = Mqtt()
mqtt.init_app(app)


'''
蓝图功能，对所有的url进行蓝图功能配置
'''

from app.views.client import client

app.register_blueprint(client, url_prefix='/client')


