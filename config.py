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

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    # sqlite
    # sqlite连接配置路径
    # SQLALCHEMY_DATABASE_URI= 'sqlite:////tmp/test.db' # sqlite

    #登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名test
    #注意:  1、使用pymysql时需要mysql+pymysql才行!!!
    #       2、mysql中首先需要创建test数据库才能用manager.py初始化model中设计的表格
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:#Redfalsh192729@localhost:3306/test'
    #设置这一项是每次请求结束后都会自动提交数据库中的变动
    SQLALCHEMY_TRACK_MODIFICATIONS=True


class TestingConfig(Config):
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
