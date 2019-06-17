#!/usr/bin/env python
# encoding: utf-8

from flask import Flask
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Sm9obiBTY2hyb20ga2lja3MgYXNz'
app.config['STRIPE_API_KEY'] = 'SmFjb2IgS2FwbGFuLU1vc3MgaXMgYSBoZXJv'

#登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名test
#注意:  1、使用pymysql时需要mysql+pymysql才行!!!
#       2、mysql中首先需要创建test数据库才能用manager.py初始化model中设计的表格
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:#Redfalsh192729@dqtttt.cn:3306/tap'
#设置这一项是每次请求结束后都会自动提交数据库中的变动
#  app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

app.config['MQTT_BROKER_URL'] = 'dqtttt.cn'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'admin'
app.config['MQTT_PASSWORD'] = 'public'
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

# 数据库初始化
db = SQLAlchemy()
db.init_app(app)
from model import User

# mqtt初始化
mqtt = Mqtt()
mqtt.init_app(app)


MQTT_SUBCRIBE = [
    ("$SYS/brokers/+/clients/#", 0),
    ("/tap/#", 0),
]

@app.route('/')
def index():
    return render_template('index.html')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(topic="$SYS/brokers/+/clients/#", qos=0)
    mqtt.subscribe(topic="/tap/#", qos=0)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
        )

if __name__ == '__main__':
    # 注意，这里要关闭自动加载器，不然flask会重启两次，mqtt会有两个客户端，会影响订阅等
    app.run(host='0.0.0.0', port=6000,use_reloader=False, debug=True)
