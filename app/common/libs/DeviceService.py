#!/usr/bin/env python
# encoding: utf-8

import hashlib,requests,random,string,json
import time
from app import  app

class MemberService():

    @staticmethod
    def geneSN( info ):
        m = hashlib.md5()
        str = "%s" % time.time()
        m.update(str.encode("utf-8"))
        return m.hexdigest()

