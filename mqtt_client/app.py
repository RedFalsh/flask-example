#!/usr/bin/env python
# encoding: utf-8

import sys
import getopt

#  from config import config
#  import configparser

#  try:
    #  opts, args = getopt.getopt(sys.argv[1:],"-h-v",["help","version","ini="])
    #  if not opts:
        #  print('usage: timer [-v|--version] [-h|--help] [--ini=<path>]')
        #  sys.exit(2)
    #  for opt_name,opt_value in opts:
        #  if opt_name in ('-h','--help'):
            #  print('usage: timer [-v|--version] [-h|--help] [--ini=<path>]')
            #  sys.exit(0)
        #  if opt_name in ('-v','--version'):
            #  print("v1.01 ")
            #  sys.exit(0)
        #  if opt_name in ('-i','--ini'):
            #  ini_file = opt_value
            #  cf = configparser.ConfigParser()
            #  cf.read(ini_file)
            #  print("timer load file: ", ini_file)
#  except getopt.GetoptError:
    #  print('usage: timer [-v|--version] [-h|--help] [--ini=<path>]')
    #  sys.exit(2)


#  conf = cf['conf']

#  SQLALCHEMY_DATABASE_URI= conf['SQLALCHEMY_DATABASE_URI']

#  MQTT_BROKER_URL  = conf['MQTT_BROKER_URL']
#  MQTT_BROKER_PORT = int(conf['MQTT_BROKER_PORT'])
#  MQTT_CLIENT_ID   = conf['MQTT_CLIENT_ID']
#  MQTT_USERNAME    = conf['MQTT_USERNAME']
#  MQTT_PASSWORD    = conf['MQTT_PASSWORD']
#  MQTT_KEEPALIVE   = int(conf['MQTT_KEEPALIVE'])
#  MQTT_TLS_ENABLED = True if conf['MQTT_TLS_ENABLED'].lower() == 'true' else False
#  MQTT_SUBCRIBE = [
    #  ("$SYS/brokers/+/clients/#", 0),
    #  ("/tap/#", 0),
#  ]

#  LOG_PATH = conf['LOG_PATH']

SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:#Redfalsh192729@dqtttt.cn:3306/tap"

MQTT_BROKER_URL  = 'dqtttt.cn'
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID   = 'xxx'
MQTT_USERNAME    = 'admin'
MQTT_PASSWORD    = 'public'
MQTT_KEEPALIVE   = 60
MQTT_TLS_ENABLED = False

MQTT_SUBCRIBE = [
    ("$SYS/brokers/+/clients/#", 0),
    ("/tap/#", 0),
]

LOG_PATH='/opt/timer.log'

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

# 数据库相关
from sqlalchemy import create_engine
from sqlalchemy import update
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

# 初始化数据库连接:
engine = create_engine(SQLALCHEMY_DATABASE_URI)
# 创建DBSession类型:
#  DBSession = sessionmaker(bind=engine)
#  session = DBSession()

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# 全局session, 用于线程外的
session = Session()

from models import Device,DeviceTime,DeviceOperateLog

# 帮助
from helper import getCurrentDate, getFormatDate


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

        schedule.every(5).seconds.do(self.timerTaskJob)

        self.run()

    def run(self):
        """ The callback for when the client receives a CONNACK response from the server.
        """
        # 连接mqtt服务器
        self.client = mqtt.Client(MQTT_CLIENT_ID)
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

        # 匹配设备上线
        connect_res = re.compile(r'^\$SYS/brokers/(.*?)/clients/([a-zA-Z0-9]{10})/(connected|disconnected)').match(topic)
        if connect_res:
            sn = connect_res.group(2)
            connect = connect_res.group(3)
            logger.info("设备%s"%sn)
            device_info = session.query(Device).filter_by( sn=sn ).first()
            if device_info:
                if connect == "connected":
                    logger.info("设备%s上线"%sn)
                    device_info.online = 1
                    self.deviceOperateLogAdd(sn,'上线','mqtt服务器')
                    # self.client.publish('/dev/%s/pub'%sn, "%s:%s"%(CMD_TAP_ONLINE, 1))
                if connect == "disconnected":
                    logger.info("设备%s掉线"%sn)
                    device_info.online = 0
                    self.deviceOperateLogAdd(sn,'下线','mqtt服务器')
                    # self.client.publish('/dev/%s/pub'%sn, "%s:%s"%(CMD_TAP_ONLINE, 0))
                session.commit()

        # 匹配设备相关操作
        operate_res = re.compile(r'^/tap/([a-zA-Z0-9]{10})/(.*)').match(topic)
        logger.info(operate_res)
        if operate_res:
            sn = operate_res.group(1)
            logger.info(sn)
            tag = operate_res.group(2)
            logger.info(tag)
            if tag == "sta1":
                logger.info("1号阀状态变化:%s"%payload)
                self.deviceStatusChanged(sn=sn, status1=payload)
                if payload == "0":
                    self.deviceOperateLogAdd(sn,'1号阀:关闭','设备')
                if payload == "1":
                    self.deviceOperateLogAdd(sn,'1号阀:开启','设备')
                if payload == "2":
                    self.deviceOperateLogAdd(sn,'1号阀:半开','设备')
            if tag == "sta2":
                logger.info("2号阀状态变化:%s"%payload)
                self.deviceStatusChanged(sn=sn, status2=payload)
                if payload == "0":
                    self.deviceOperateLogAdd(sn,'2号阀:关闭','设备')
                if payload == "1":
                    self.deviceOperateLogAdd(sn,'2号阀:开启','设备')
                if payload == "2":
                    self.deviceOperateLogAdd(sn,'2号阀:半开','设备')

    def deviceOperateLogAdd(self, sn, msg, source):
        device_info = session.query(Device).filter_by( sn=sn ).first()
        logger.info(device_info)
        if device_info:
            operate_log = DeviceOperateLog()
            operate_log.device_id = device_info.id
            operate_log.msg = msg
            operate_log.source = source
            operate_log.time = getCurrentDate()
            session.add(operate_log)
            session.commit()
            logger.info("添加记录完成")

    def deviceStatusChanged(self, sn="", status1=None, status2=None):
        device_info = session.query(Device).filter_by( sn=sn ).first()
        if device_info:
            # 1号阀门状态
            if status1 is not None:
                device_info.status1 = int(status1)
            # 2号阀门状态
            if status2 is not None:
                device_info.status2 = int(status2)
            session.commit()
            logger.info("阀门状态变化: %s>>>\tstatus1:%s\tstatus2:%s "%(sn, status1, status2))

    def deviceControlTap(self, num, device_id, cmd):
        resp = {}
        device_info = session.query(Device).filter_by( id=device_id ).first()
        if device_info:
            if device_info.online == 1:
                sn = device_info.sn
                if num == 1:
                    self.client.publish('/tap/%s/sw1'%sn, cmd, 2)
                if num == 2:
                    self.client.publish('/tap/%s/sw2'%sn, cmd, 2)
                logger.info("mqtt推送消息......")
                return True

    def timerTask(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def timerTaskJob(self):
        logger.info("执行定时任务......")
        # 线程中使用session需要添加一个新的对象来进行执行
        tmp_session = Session()
        time_now = getFormatDate(format="%H:%M")
        time_week = getFormatDate(format="%w")
        time_info = tmp_session.query(DeviceTime).filter_by( alive=1 ).all()
        for t in time_info:
            logger.info(t.open_time)
            if t.type == 1: # 执行一次的任务
                if t.open_time == time_now:
                    if t.open_flag == 0:
                        if self.deviceControlTap(t.switch_num, t.device_id, 'ON'):
                            t.open_flag = 1
                            tmp_session.commit()
                if t.close_time == time_now:
                    if t.close_flag == 0:
                        if self.deviceControlTap(t.switch_num, t.device_id, 'OFF'):
                            t.close_flag = 1
                            tmp_session.commit()
                if t.open_flag == 1 and t.close_flag == 1:
                    # 单次任务的执行步骤完成, 关闭任务
                    t.alive = 0
                    tmp_session.commit()
            else: # 其他周期性的任务，按星期来执行
                period = str(t.period).split(',')
                if time_week == '0':
                    time_week = '7'
                if time_week in period:
                    if t.open_time == time_now:
                        self.deviceControlTap(t.switch_num, t.device_id, 'ON')
                    if t.close_time == time_now:
                        self.deviceControlTap(t.switch_num, t.device_id, 'OFF')
        Session.remove()




if __name__ == "__main__":
    mq = MqttClient()


