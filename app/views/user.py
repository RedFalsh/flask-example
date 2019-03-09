#!/usr/bin/env python
# encoding: utf-8

from flask import Blueprint, render_template

route_user = Blueprint('user_page', __name__,
        template_folder='templates',
        static_folder='static')

@route_user.route('login')
def login():
    return "login"
