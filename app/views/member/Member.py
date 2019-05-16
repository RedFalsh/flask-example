#!/usr/bin/env python
# encoding: utf-8

from flask import Blueprint, render_template

from app import db

member = Blueprint('member', __name__,
                 template_folder='templates',
                 static_folder='static')

@member.route('/info')
def index():
    return 'member info'

# @home.route('home')
# def index_html():
    # return render_template('home/index.html')


