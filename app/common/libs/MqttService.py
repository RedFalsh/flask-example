#!/usr/bin/env python
# encoding: utf-8

import hashlib,requests,random,string,json
from app import  app

class MqttService():

    @staticmethod
    def getConnections( clientid ):
        """
        功能: 从mqtt服务器中获取客户端连接信息
        api: GET api/v3/connections/${clientid}
        """
        url = app.config['MQTT_SERVER_BASE_URLS'] + 'api/v3/connections/%s'%(clientid)
        r = requests.get(url, auth=(app.config['MQTT_SERVER_USER'],app.config['MQTT_SERVER_PASSWORD']))
        res = json.loads(r.text)
        if res['data']:
            return 1
        else:
            return 0
        return 0


    @staticmethod
    def getConnectionsByNode( clientid ):
        """
        功能: 从mqtt服务器中通过节点服务器获取客户端连接信息
        api: GET api/v3/${nodes}/connections/${clientid}
        """
        url = app.config['MQTT_SERVER_BASE_URLS'] + 'api/v3/nodes/%s/connections/%s'%(app.config['MQTT_SERVER_NODE'], clientid)
        r = requests.get(url, auth=(app.config['MQTT_SERVER_USER'],app.config['MQTT_SERVER_PASSWORD']))
        res = json.loads(r.text)
        return res


