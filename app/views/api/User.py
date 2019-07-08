#!/usr/bin/env python
# encoding: utf-8

from app.views.api import route_api
from  flask import request,jsonify,g
import requests,json

from app import db
from app.model import User

from app.common.libs.Logging import logger
from app.common.libs.UserService import UserService
from app.common.libs.Helper import getCurrentDate


@route_api.route("/user/login",methods = [ "GET","POST" ])
def userLogin():
    resp = { 'code':20000,'data':{}}
    req = request.values

    data = json.loads(req['data']) if 'data' in req else ''
    if not data:
        resp['code'] = -1
        resp['message'] = "信息错误~"
        return jsonify(resp)
    username = data['username']
    password = data['password']
    if not username:
        resp['code'] = -1
        resp['message'] = "请填写用户名~"
        return jsonify(resp)
    if not password:
        resp['code'] = -1
        resp['message'] = "请填写密码~"
        return jsonify(resp)

    user_info = User.query.filter_by( login_name = username ).first()
    if not user_info:
        resp['code'] = -1
        resp['message'] = "用户未注册~"
        return jsonify(resp)

    # 校验密码是否正确
    if not user_info.login_pwd == UserService.genePwd(password,user_info.login_salt):
        resp['code'] = -1
        resp['message'] = "用户名或密码错误~"
        return jsonify(resp)

    token = "%s#%s" % (UserService.geneAuthCode(user_info), user_info.id)
    resp['data'] = {'token': token}
    return jsonify( resp )

@route_api.route("/user/register",methods = [ "GET","POST" ])
def userRegister():
    resp = { 'code':20000 ,'message':'注册成功~','data':{} }
    data = request.get_data()
    if not data:
        resp['code'] = -1
        resp['message'] = "need application/x-www-form-urlencoded~"
        return jsonify(resp)

    form = json.loads(data)
    username = form['username'] if 'username' in form else ''
    password = form['password'] if 'password' in form else ''

    if not username:
        resp['code'] = -1
        resp['message'] = "请填写用户名~"
        return jsonify(resp)
    if not password:
        resp['code'] = -1
        resp['message'] = "请填写密码~"
        return jsonify(resp)

    user_info = User.query.filter_by( login_name = username ).first()
    if user_info:
        resp['code'] = -1
        resp['message'] = "用户名:%s 已存在~"%username
        return jsonify(resp)
    model_user = User()
    model_user.login_name = username
    model_user.status = 1
    model_user.login_salt = UserService.geneSalt()
    model_user.login_pwd = UserService.genePwd(password, model_user.login_salt)
    model_user.updated_time = model_user.created_time = getCurrentDate()
    db.session.add(model_user)
    db.session.commit()
    return jsonify( resp )

@route_api.route("/user/info",methods = [ "GET","POST" ])
def userInfo():
    resp = { 'code':20000,'data':{}}
    req = request.values
    token = req['token'] if 'token' in req else ''
    if not token:
        resp['code'] = -1
        resp['message'] = "need token~"
        return jsonify(resp)

    auth_info = token.split("#")
    if len(auth_info) != 2:
        resp['code'] = -1
        resp['message'] = "token err~"
        return jsonify(resp)
    try:
        user_info = User.query.filter_by(id=auth_info[1]).first()
    except Exception:
        resp['code'] = -1
        resp['message'] = "token err~"
        return jsonify(resp)

    if auth_info[0] != UserService.geneAuthCode( user_info ):
        resp['code'] = -1
        resp['message'] = "token err~"
        return jsonify(resp)

    resp['data'] = {"roles": user_info.roles.split(';'),
                    "introduction":user_info.introduction,
                    "avatar": user_info.avatar,
                    "name": user_info.nickname}

    return jsonify( resp )

@route_api.route("/user/logout",methods = [ "GET","POST" ])
def userLogout():
    resp = { 'code':20000,'data':{}}
    return jsonify( resp )

