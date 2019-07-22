#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#  from flask_mqtt import Mqtt
from config import config
from flask_cors import CORS
import os

# app初始化,
# instance_relative_config 设置config文件可从Instance文件中查找
app = Flask(__name__, instance_relative_config=True)

# 配置文件导入
if "TAP_WEB" in os.environ:
    app.config.from_object(config[os.environ['TAP_WEB']])
    print("当前系统环境变量值:%s"%os.environ['TAP_WEB'])
else:
    print("请设置系统环境变量: TAP_WEB")

# 数据库管理
db = SQLAlchemy()
db.init_app(app)

# 跨域问题
cors = CORS()
cors.init_app(app, supports_credentials=True)

# 后面需要调用db的，导入时需要放在db初始化完成之后
from app.admin import admin

admin.init_app(app)

'''
统一拦截处理和统一错误处理
'''
from app.interceptor.ApiInterceptor import  *

'''
蓝图功能，对所有的url进行蓝图功能配置
'''

from app.views.home import home
from app.views.api import route_api

app.register_blueprint(home, url_prefix='/')
app.register_blueprint(route_api, url_prefix='/api')


