# coding: utf-8

from sqlalchemy import Column, DateTime, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Device(Base):
    __tablename__ = 'device'

    id = Column(INTEGER(11), primary_key=True)
    member_id = Column(INTEGER(11))
    name = Column(String(30))
    sn = Column(String(32))
    type = Column(String(20))
    img = Column(String(200))
    position = Column(String(200))
    online = Column(INTEGER(11))
    status = Column(INTEGER(11))
    sub = Column(String(50))
    pub = Column(String(50))
    updated_time = Column(DateTime)
    created_time = Column(DateTime)


class DeviceControl(Base):
    __tablename__ = 'device_control'

    id = Column(INTEGER(11), primary_key=True)
    device_id = Column(INTEGER(11))
    cmd = Column(INTEGER(11))
    cmd_hex = Column(String(10))
    msg = Column(String(10))
    time = Column(DateTime)


class DeviceMqtt(Base):
    __tablename__ = 'device_mqtt'

    id = Column(INTEGER(11), primary_key=True)
    device_id = Column(INTEGER(11))
    server = Column(String(100))
    port = Column(INTEGER(11))
    login_user = Column(String(20))
    login_pwd = Column(String(30))
    sub = Column(String(50))
    pub = Column(String(50))
    updated_time = Column(DateTime)
    created_time = Column(DateTime)


class DeviceOperateLog(Base):
    __tablename__ = 'device_operate_log'

    id = Column(INTEGER(11), primary_key=True)
    device_id = Column(INTEGER(11))
    code = Column(INTEGER(11))
    msg = Column(String(20))
    source = Column(String(50))
    time = Column(DateTime)


class DeviceTime(Base):
    __tablename__ = 'device_time'

    id = Column(INTEGER(11), primary_key=True)
    device_id = Column(INTEGER(11))
    alive = Column(INTEGER(11))
    type = Column(INTEGER(11))
    period = Column(String(30))
    open_time = Column(String(20))
    open_flag = Column(INTEGER(11))
    close_time = Column(String(20))
    close_flag = Column(INTEGER(11))
    updated_time = Column(DateTime)
    created_time = Column(DateTime)


class Member(Base):
    __tablename__ = 'member'

    id = Column(INTEGER(11), primary_key=True)
    nickname = Column(String(100))
    mobile = Column(String(11))
    sex = Column(INTEGER(11))
    avatar = Column(String(200))
    salt = Column(String(32))
    reg_ip = Column(String(100))
    status = Column(INTEGER(11))
    updated_time = Column(DateTime)
    created_time = Column(DateTime)


class OauthMemberBind(Base):
    __tablename__ = 'oauth_member_bind'
    __table_args__ = (
        Index('idx_type_openid', 'type', 'openid'),
    )

    id = Column(INTEGER(11), primary_key=True)
    member_id = Column(INTEGER(11))
    client_type = Column(String(20))
    type = Column(INTEGER(11))
    openid = Column(String(80))
    unionid = Column(String(100))
    extra = Column(Text)
    updated_time = Column(DateTime)
    created_time = Column(DateTime)


class User(Base):
    __tablename__ = 'user'

    id = Column(BIGINT(20), primary_key=True)
    nickname = Column(String(100))
    mobile = Column(String(20))
    email = Column(String(100))
    sex = Column(INTEGER(11))
    avatar = Column(String(64))
    login_name = Column(String(20), unique=True)
    login_pwd = Column(String(32))
    login_salt = Column(String(32))
    status = Column(INTEGER(11))
    updated_time = Column(DateTime)
    created_time = Column(DateTime)
