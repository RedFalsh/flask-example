#!/usr/bin/env python
# encoding: utf-8

from app import db

class User(db.Model):
    __tablename__ = 'user'

    id          = db.Column(db.BigInteger, primary_key=True)
    nickname     = db.Column(db.String(100))
    mobile       = db.Column(db.String(20))
    email        = db.Column(db.String(100))
    sex          = db.Column(db.Integer)
    avatar       = db.Column(db.String(64))
    login_name   = db.Column(db.String(20), unique=True)
    login_pwd    = db.Column(db.String(32))
    login_salt   = db.Column(db.String(32))
    status       = db.Column(db.Integer)
    updated_time = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime)

    #  def __init__(self, name, password, telephone):
        #  self.name = name
        #  self.password = password
        #  self.telephone = telephone

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Member(db.Model):
    __tablename__ = 'member'

    id           = db.Column(db.Integer, primary_key=True)
    nickname     = db.Column(db.String(100))
    mobile       = db.Column(db.String(11))
    sex          = db.Column(db.Integer)
    avatar       = db.Column(db.String(200))
    salt         = db.Column(db.String(32))
    reg_ip       = db.Column(db.String(100))
    status       = db.Column(db.Integer)
    updated_time = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime)

class OauthMemberBind(db.Model):
    __tablename__ = 'oauth_member_bind'
    __table_args__ = (
        db.Index('idx_type_openid', 'type', 'openid'),
    )

    id           = db.Column(db.Integer, primary_key=True)
    member_id    = db.Column(db.Integer)
    client_type  = db.Column(db.String(20))
    type         = db.Column(db.Integer)
    openid       = db.Column(db.String(80))
    unionid      = db.Column(db.String(100))
    extra        = db.Column(db.Text)
    updated_time = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime)

class Device(db.Model):
    __tablename__ = 'device'

    id           = db.Column(db.Integer, primary_key=True)
    member_id    = db.Column(db.Integer)
    name         = db.Column(db.String(30))
    number       = db.Column(db.String(30))
    sn           = db.Column(db.String(32))
    type         = db.Column(db.String(20))
    img          = db.Column(db.String(200))
    tag          = db.Column(db.String(30))
    position     = db.Column(db.String(200))
    online       = db.Column(db.Integer)
    sub          = db.Column(db.String(50))
    pub          = db.Column(db.String(50))

    status       = db.Column(db.Integer)

    alias1       = db.Column(db.String(30))
    status1      = db.Column(db.Integer)

    alias2       = db.Column(db.String(30))
    status2      = db.Column(db.Integer)

    updated_time = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime)

class DeviceTap(db.Model):
    __tablename__ = 'device_tap'

    id           = db.Column(db.Integer, primary_key=True)
    device_id    = db.Column(db.Integer)
    name         = db.Column(db.String(30))
    status       = db.Column(db.Integer)


class DeviceMqtt(db.Model):
    __tablename__ = 'device_mqtt'

    id           = db.Column(db.Integer, primary_key=True)
    device_id    = db.Column(db.Integer)
    server       = db.Column(db.String(100))
    port         = db.Column(db.Integer)
    login_user   = db.Column(db.String(20))
    login_pwd    = db.Column(db.String(30))
    sub          = db.Column(db.String(50))
    pub          = db.Column(db.String(50))
    updated_time = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime)

class DeviceTime(db.Model):
    __tablename__ = 'device_time'

    id           = db.Column(db.Integer, primary_key=True)
    device_id    = db.Column(db.Integer)
    alive        = db.Column(db.Integer)
    type         = db.Column(db.Integer)
    switch_num   = db.Column(db.Integer)
    period       = db.Column(db.String(30))
    open_time    = db.Column(db.String(20))
    open_flag    = db.Column(db.Integer)
    close_time   = db.Column(db.String(20))
    close_flag   = db.Column(db.Integer)
    updated_time = db.Column(db.DateTime)
    created_time = db.Column(db.DateTime)

class DeviceOperateLog(db.Model):
    __tablename__ = 'device_operate_log'

    id        = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer)
    code       = db.Column(db.Integer)
    msg       = db.Column(db.String(20))
    source    = db.Column(db.String(50))
    time      = db.Column(db.DateTime)

class DeviceControl(db.Model):
    __tablename__ = 'device_control'

    id        = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer)
    cmd       = db.Column(db.Integer)
    cmd_hex   = db.Column(db.String(10))
    msg       = db.Column(db.String(10))
    time      = db.Column(db.DateTime)

