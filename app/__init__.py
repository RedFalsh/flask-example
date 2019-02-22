#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# app初始化
myapp = Flask(__name__)

# 数据库管理
db = SQLAlchemy()

def create_app(config_name):
    # 导入配置文件
    from config import config
    myapp.config.from_object(config[config_name])

    # 后台管理数据库 admin
    from app.admin import admin
    admin.init_app(myapp)

    # 数据库配置初始化
    db.init_app(myapp)

    from app.views.home import home
    myapp.register_blueprint(home)

    return myapp

if __name__ == '__main__':
    app = create_app('development')
    app.run()

