#!/usr/bin/env python
# encoding: utf-8

import hashlib,requests,random,string,json
import time
from app import db
from app.model import Device
from app.model import Member

from app.common.libs.Helper import getCurrentDate, getFormatDate

from sqlalchemy import func, desc

class DeviceService():

    @staticmethod
    def geneSN( info ):
        m = hashlib.md5()
        str = "%s" % time.time()
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def filterDeviceByEditor(req):
        resp = { 'code':20000, 'message':'查询成功', 'data':{}}
        mobile = req['mobile'] if 'mobile' in req else ''
        sn = req['sn'] if 'sn' in req else ''
        page = int( req['page'] ) if 'page' in req else 0
        limit = int( req['limit'] ) if 'limit' in req else 0
        offset = ( page - 1 ) * limit

        #  rule = func.concat(Device.sn, Device.position).op('regexp')('.*%s.*'%keywords.replace(' ','.*'))

        query = Device.query.filter( Device.member_id == Member.id)\
                            .filter( Member.mobile.like('%%%s%%'%mobile) )\
                            .filter( Device.sn.like('%%%s%%'%sn))

        total = query.count()
        tap_list = query.offset( offset ).limit( limit ).all()

        items = []
        for tap in tap_list:
            items.append({
                'name': tap.name,
                'number':tap.number,
                'position':tap.position,
                'sn': tap.sn,
                'power': str(tap.power),
                'online': tap.online,
                'status1': tap.status1,
                'status2': tap.status2,
                'alias1': tap.alias1,
                'alias2': tap.alias2,
                'created_time': getFormatDate(tap.created_time),
            })

        resp['data']['items'] = items
        resp['data']['total'] = total

        return resp

    @staticmethod
    def filterDeviceByUser(req, user_info):
        resp = { 'code':20000, 'message':'查询成功', 'data':{}}

        position = req['position'] if 'position' in req else ''
        page = int( req['page'] ) if 'page' in req else 0
        limit = int( req['limit'] ) if 'limit' in req else 0
        offset = ( page - 1 ) * limit

        query = Device.query\
            .filter( Member.id == Device.member_id )\
            .filter( Member.mobile == user_info.mobile )\
            .filter( Device.position.like('%' + position + '%') )

        total = query.count()
        tap_list = query.offset( offset ).limit( limit ).all()

        items = []
        for tap in tap_list:
            items.append({
                'name': tap.name,
                'number':tap.number,
                'position':tap.position,
                'sn': tap.sn,
                'power': str(tap.power),
                'online': tap.online,
                'status1': tap.status1,
                'status2': tap.status2,
                'alias1': tap.alias1,
                'alias2': tap.alias2,
                'created_time': getFormatDate(tap.created_time),
            })

        resp['data']['items'] = items
        resp['data']['total'] = total

        return resp

    @staticmethod
    def tapInfo(sn = ''):
        resp = { 'code':20000, 'message':'查询成功', 'data':{}}
        res = db.session.query(Device, Member)\
            .filter( Member.id == Device.member_id )\
            .filter( Device.sn == sn )\
            .first()
        if not res:
            resp['code'] = -1
            resp['message'] = "信息查询错误"
            return jsonify(resp)

        tap = res[0]
        tap_info = {
            'name': tap.name,
            'number':tap.number,
            'position':tap.position,
            'sn': tap.sn,
            'power': str(tap.power),
            'online': tap.online,
            'status1': tap.status1,
            'status2': tap.status2,
            'alias1': tap.alias1,
            'alias2': tap.alias2,
            'created_time': getFormatDate(tap.created_time)
        }
        member = res[1]
        user_info = {
            'nickname': member.nickname,
            'mobile': member.mobile,
            'sex': member.sex,
            'avatar': member.avatar
        }

        resp['data']['tap_info'] = tap_info
        resp['data']['user_info'] = user_info

        return resp


