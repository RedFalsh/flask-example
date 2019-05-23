#!/usr/bin/env python
# encoding: utf-8

"""

A small Test application to show how to use Flask-MQTT.

"""

import json,time,threading
from flask import Flask, render_template
from flask_mqtt import Mqtt
#  from flask_socketio import SocketIO

# eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'admin'
app.config['MQTT_PASSWORD'] = 'public'
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

mqtt = Mqtt()
mqtt.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

def runn():
    print("开启定时器")
    while True:
        time.sleep(3)
        print("run")

time_thread = threading.Thread(target=runn)
time_thread.setDaemon(True)
time_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
