#!/usr/bin/env python
# encoding: utf-8


from config import config
# 数据库相关
# 导入:
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

# 初始化数据库连接:
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
# 创建DBSession类型:
#  DBSession = sessionmaker(bind=engine)
#  session = DBSession()

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
