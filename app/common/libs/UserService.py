#!/usr/bin/env python
# encoding: utf-8


import hashlib,base64,random,string
from app import db
from app.model import User

class UserService():

    @staticmethod
    def geneAuthCode(user_info = None ):
        m = hashlib.md5()
        str = "%s-%s-%s-%s" % (user_info.id, user_info.login_name, user_info.login_pwd, user_info.login_salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def genePwd( pwd,salt):
        m = hashlib.md5()
        str = "%s-%s" % ( base64.encodebytes( pwd.encode("utf-8") ) , salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def geneSalt( length = 16 ):
        keylist = [ random.choice( ( string.ascii_letters + string.digits ) ) for i in range( length ) ]
        return ( "".join( keylist ) )

    @staticmethod
    def getUserInfo(request):
        user_id = str(request.headers['X-Token']).split('#')[1]
        electronic_info =  User.query.filter_by( id = user_id  ).first()
        if not electronic_info:
            return False
        return electronic_info



