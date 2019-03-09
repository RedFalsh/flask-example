#!/usr/bin/env python
# encoding: utf-8


from flask import Blueprint, render_template

from app import db

#  home = Blueprint('home', __name__, url_prefix='/home',
                                    #  template_folder='templates',
                                    #  static_folder='static')

home = Blueprint('home', __name__,
                 template_folder='templates',
                 static_folder='static')

@home.route('/')
def index():
    return 'Whelecome My Flask Example'

# @home.route('home')
# def index_html():
    # return render_template('home/index.html')


