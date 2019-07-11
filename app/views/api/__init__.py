#!/usr/bin/env python
# encoding: utf-8


from flask import Blueprint
route_api = Blueprint( 'api_page',__name__ )

from app.views.api.User import *
from app.views.api.Member import *
from app.views.api.Device import *
from app.views.api.web.Tap import *


@route_api.route("/")
def index():
    return "Mina Api V1.0~~"
