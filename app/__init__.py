#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# app初始化,
# instance_relative_config 设置config文件可从Instance文件中查找
myapp = Flask(__name__, instance_relative_config=True)

# 数据库管理
db = SQLAlchemy()

def create_app(config_name):
    # 导入配置文件
    import os
    myapp.config.from_pyfile('base_setting.py')
    if "ops_config" in os.environ:
        myapp.config.from_pyfile('%s_setting.py'%os.environ['ops_config'])

    # 后台管理数据库 admin
    from app.admin import admin
    admin.init_app(myapp)

    # 数据库配置初始化
    db.init_app(myapp)

    from app.views.home import home
    from app.views.user import route_user
    myapp.register_blueprint(home, url_prefix='/')
    myapp.register_blueprint(route_user, url_prefix='/user')

    return myapp

if __name__ == '__main__':
    app = create_app('development')
    app.run()

