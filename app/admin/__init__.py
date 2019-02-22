#!/usr/bin/env python
# encoding: utf-8


from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose

from app.model import User, db

admin = Admin(name='后台管理', template_mode = 'bootstrap3')

class UserModelAdmin(ModelView):
    can_create = False  # disable model create
    can_edit = False  # disable model edit
    can_delete = False  # disable model delete
    can_view_details = False  # 显示细节

    # 可姓名、电话进行搜索
    column_searchable_list = ['name', 'telephone']
    # 按名字过滤
    column_filters = ['name']

    column_labels = {
        'name':'姓名',
        'password':'密码',
        'telephone':'电话',
    }

# 将新建的UserModelAdmin添加到admin中
admin.add_view(UserModelAdmin(User, db.session, category='用户'))


