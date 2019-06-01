#!/usr/bin/env python
# encoding: utf-8

import sys
import getopt

#  from config import config
import configparser

try:
    opts, args = getopt.getopt(sys.argv[1:],"-h-v",["help","version","ini="])
    if not opts:
        print('usage: timer [-v|--version] [-h|--help] [--ini=<path>]')
        sys.exit(2)
    for opt_name,opt_value in opts:
        if opt_name in ('-h','--help'):
            print('usage: timer [-v|--version] [-h|--help] [--ini=<path>]')
            sys.exit(0)
        if opt_name in ('-v','--version'):
            print("v1.01 ")
            sys.exit(0)
        if opt_name in ('-i','--ini'):
            ini_file = opt_value
            cf = configparser.ConfigParser()
            cf.read(ini_file)
            print("timer load file: ", ini_file)
except getopt.GetoptError:
    print('usage: timer [-v|--version] [-h|--help] [--ini=<path>]')
    sys.exit(2)


conf = cf['conf']

SQLALCHEMY_DATABASE_URI= conf['SQLALCHEMY_DATABASE_URI']

MQTT_BROKER_URL  = conf['MQTT_BROKER_URL']
MQTT_BROKER_PORT = int(conf['MQTT_BROKER_PORT'])
MQTT_CLIENT_ID   = conf['MQTT_CLIENT_ID']
MQTT_USERNAME    = conf['MQTT_USERNAME']
MQTT_PASSWORD    = conf['MQTT_PASSWORD']
MQTT_KEEPALIVE   = int(conf['MQTT_KEEPALIVE'])
MQTT_TLS_ENABLED = True if conf['MQTT_TLS_ENABLED'].lower() == 'true' else False
MQTT_SUBCRIBE = [
    ("$SYS/brokers/emqx@127.0.0.1/clients/#", 0),
    ("/dev/#", 0),
]

CMD_TAP_OPEN     = int(conf['CMD_TAP_OPEN'], 16)
CMD_TAP_CLOSE    = int(conf['CMD_TAP_CLOSE'], 16)
CMD_TAP_STATUS   = int(conf['CMD_TAP_STATUS'], 16)
CMD_TAP_ONLINE   = int(conf['CMD_TAP_ONLINE'], 16)
CMD_TAP_POWER    = int(conf['CMD_TAP_POWER'], 16)
CMD_TAP_SET_TIME = int(conf['CMD_TAP_SET_TIME'], 16)

LOG_PATH = conf['LOG_PATH']

# 日志文件
import logging
#  logging.basicConfig(level = logging.INFO,
                    #  filename=LOG_PATH,
                    #  filemode='a',
                    #  format = '[%(asctime)s] - %(levelname)s - %(message)s')
#  logger = logging.getLogger(__name__)

# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler(LOG_PATH)
fh.setLevel(logging.INFO)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# 定义handler的输出格式
formatter = logging.Formatter('[%(asctime)s][%(filename)s][line: %(lineno)d][%(levelname)s]: %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

# 记录一条日志
logger.info('starting')


# 帮助
from helper import getCurrentDate, getFormatDate

# 数据库相关
# from sql import session
from sql import Session
session = Session()

from model import Device,DeviceTime,DeviceOperateLog

# mqtt相关
import paho.mqtt.client as mqtt
import re
import json
import time
import threading
import schedule

class MqttClient(object):

    regex = {
        'connect': re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{10})/(connected|disconnected)'),
        'operate': re.compile(r'^/dev/([a-zA-Z0-9]{10})/(sub|pub)')
    }

    def __init__(self):
        self.time_thread = threading.Thread(target=self.timerTask)
        self.time_thread.setDaemon(True)
        self.time_thread.start()

        schedule.every(30).seconds.do(self.timerTaskJob)

        self.run()

    def run(self):
        """ The callback for when the client receives a CONNACK response from the server.
        """
        # 连接mqtt服务器
        self.client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER_URL, MQTT_BROKER_PORT, MQTT_KEEPALIVE)
        self.client.loop_forever()

    def on_connect(self,client, userdata, flags, rc):
        # 此处订阅所有设备的route
        logger.info("Connected with result code "+str(rc))
        self.client.subscribe(MQTT_SUBCRIBE)

    def on_message(self, client, userdata, msg):
        """ The callback for when a PUBLISH message is received from the server.
        """
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        logger.info("监听到到消息------>:")
        logger.info("topic:"+topic)
        logger.info("payload:"+payload)

        connect_res = self.regex['connect'].match(topic)
        if connect_res:
            sn = connect_res.group(2)
            connect = connect_res.group(3)
            resp = {'code': CMD_TAP_ONLINE}

            device_info = session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                if connect == "connected":
                    device_info.online = 1
                    resp['msg'] = 1
                if connect == "disconnected":
                    device_info.online = 0
                    resp['msg'] = 0
                session.commit()
                self.client.publish('/dev/%s/pub'%sn, json.dumps(resp))

        operate_res = self.regex['operate'].match(topic)
        if operate_res:
            sn = operate_res.group(1)
            sub_pub = operate_res.group(2)
            payload = json.loads(payload)

            code = int(payload['code']) if 'code' in payload else ''
            msg = payload['msg'] if 'msg' in payload else ''

            logger.info("设备操作记录:")
            if sub_pub == 'sub':
                logger.info("user->device: %s"%payload)
                self.deviceOperateLogAdd(sn,code,msg,'小程序')
            if sub_pub == 'pub':
                logger.info("device->user: %s"%payload)
                self.deviceOperateLogAdd(sn,code,msg,'小程序')

            # 监听到阀门状态变化
            if int(code) == CMD_TAP_STATUS:
                self.deviceStatusChanged(sn, int(msg))

    def deviceOperateLogAdd(self, sn, code, msg, source):
        device_info = session.query(Device).filter_by( sn=sn ).first()
        if device_info:
            operate_log = DeviceOperateLog()
            operate_log.device_id = device_info.id
            operate_log.code = code
            operate_log.msg = msg
            operate_log.source = source
            operate_log.time = getCurrentDate()
            session.add(operate_log)
            session.commit()

    def deviceStatusChanged(self, sn, status):
        device_info = session.query(Device).filter_by( sn=sn ).first()
        if device_info:
            device_info.status = status
            session.commit()
            logger.info("阀门状态变化:%s"%msg)

    def deviceControlTap(self, id, cmd):
        resp = {}
        device_info = session.query(Device).filter_by( id=id ).first()
        if device_info:
            if device_info.online == 1:
                resp['code'] = cmd
                sn = device_info.sn
                self.client.publish('/dev/%s/sub'%sn, json.dumps(resp))
                logger.info("mqtt推送消息......")
                return True

    def timerTask(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def timerTaskJob(self):
        logger.info("执行定时任务......")
        # 线程中使用session需要添加一个新的对象来进行执行
        session = Session()
        time_now = getFormatDate(format="%H:%M")
        time_week = getFormatDate(format="%w")
        time_info = session.query(DeviceTime).filter_by( alive=1 ).all()
        for t in time_info:
            logger.info(t.open_time)
            if t.type == 1: # 执行一次的任务
                if t.open_time == time_now:
                    if t.open_flag == 0:
                        if self.deviceControlTap(t.device_id, CMD_TAP_OPEN):
                            t.open_flag = 1
                            session.commit()
                if t.close_time == time_now:
                    if t.close_flag == 0:
                        if self.deviceControlTap(t.device_id, CMD_TAP_CLOSE):
                            t.close_flag = 1
                            session.commit()
                if t.open_flag == 1 and t.close_flag == 1:
                    # 单次任务的执行步骤完成, 关闭任务
                    t.alive = 0
                    session.commit()
            else: # 其他周期性的任务，按星期来执行
                period = str(t.period).split(',')
                if time_week == '0':
                    time_week = '7'
                if time_week in period:
                    if t.open_time == time_now:
                        self.deviceControlTap(t.device_id, CMD_TAP_OPEN)
                    if t.close_time == time_now:
                        self.deviceControlTap(t.device_id, CMD_TAP_CLOSE)
        Session.remove()




if __name__ == "__main__":
    mq = MqttClient()


