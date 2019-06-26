#!/usr/bin/env python
# encoding: utf-8


from app.views.api import route_api
from flask import request,jsonify,g,session
import json
from app import app,db
from app.common.libs.MemberService import MemberService, WXBizDataCrypt
from app.common.libs.Helper import getCurrentDate

from app.model import Member
from app.model import OauthMemberBind

@route_api.route("/member/login",methods = [ "GET","POST" ])
def login():
    resp = { 'code':200 ,'msg':'ok~','data':{} }
    req = request.values
    req = json.loads(req['data'])
    code = req['code'] if 'code' in req else ''
    if not code or len( code ) < 1:
        resp['code'] = -1
        resp['msg'] = "need code"
        return jsonify(resp)


    openid = MemberService.getWeChatOpenId( code )
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "use wx error"
        return jsonify(resp)

    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else 0
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''
    '''
        判断是否已经测试过，注册了直接返回一些信息
    '''
    bind_info = OauthMemberBind.query.filter_by( openid = openid,type = 1 ).first()
    if not bind_info:
        model_member = Member()
        model_member.nickname = nickname
        model_member.status = 1
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.salt = MemberService.geneSalt()
        model_member.updated_time = model_member.created_time = getCurrentDate()
        db.session.add(model_member)
        db.session.commit()

        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id
        model_bind.type = 1
        model_bind.openid = openid
        model_bind.extra = ''
        model_bind.updated_time = model_bind.created_time = getCurrentDate()
        db.session.add(model_bind)
        db.session.commit()

        bind_info = model_bind

    member_info = Member.query.filter_by(id = bind_info.member_id).first()
    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)
    resp['data'] = {'token': token}
    return jsonify( resp )


@route_api.route("/member/check-reg",methods = [ "GET","POST" ])
def checkReg():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values
    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "need code"
        return jsonify(resp)

    openid,session_key = MemberService.getWeChatOpenId(code)
    session['session_key'] = session_key
    print(session)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "use wx error"
        return jsonify(resp)

    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    if not bind_info:
        resp['code'] = -1
        resp['msg'] = "no bind"
        return jsonify(resp)

    member_info = Member.query.filter_by( id = bind_info.member_id).first()
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "not find bind information"
        return jsonify(resp)

    token = "%s#%s"%( MemberService.geneAuthCode( member_info ),member_info.id )
    resp['data'] = { 'token':token,'session_key':session_key }
    return jsonify(resp)

@route_api.route("/member/share",methods = [ "POST" ])
def memberShare():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values
    url = req['url'] if 'url' in req else ''
    member_info = g.member_info
    model_share = WxShareHistory()
    if member_info:
        model_share.member_id = member_info.id
    model_share.share_url = url
    model_share.created_time = getCurrentDate()
    db.session.add(model_share)
    db.session.commit()
    return jsonify(resp)


@route_api.route("/member/info")
def memberInfo():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    member_info = g.member_info
    resp['data']['info'] = {
        "nickname":member_info.nickname,
        "mobile":member_info.mobile,
        "avatar_url":member_info.avatar
    }
    return jsonify(resp)

@route_api.route("/member/getPhoneNumber")
def memberGetPhoneNumber():
    resp = {'code': 200, 'msg': 'ok~', 'data': {}}
    req = request.values
    appId = app.config["MINA_APP"]["appid"]
    encryptedData = req['encryptedData'] if 'encryptedData' in req else ''
    sessionKey = req['sessionKey'] if 'sessionKey' in req else ''
    iv = req['iv'] if 'iv' in req else ''
    try:
        pc = WXBizDataCrypt(appId, sessionKey)
    except Exception:
        resp['code'] = -1
        resp['msg'] = "获取手机号码错误，参数错误!"
        return jsonify(resp)

    info = pc.decrypt(encryptedData, iv)

    member_info = g.member_info
    member_info.mobile = info['phoneNumber']
    db.session.commit()

    resp['data'] = {'phoneNumber':info['phoneNumber']}

    return jsonify(resp)
