#!/usr/bin/env python
# encoding: utf-8


from flask import Blueprint
route_mqtt = Blueprint( 'mqtt_page',__name__ )

from app.views.mqttc.Client import *

@route_mqtt.route("/")
def index():
    return "mqtt v1.0"
