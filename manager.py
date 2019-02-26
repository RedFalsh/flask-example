#!/usr/bin/env python
# encoding: utf-8

import os
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db


app = create_app('development')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('runserver', Server())
manager.add_command('db', MigrateCommand)

@manager.shell
def make_shell_context():
    """Create a python CLI.

    return: Default import object
    type: `Dict`
    """
    # 确保有导入 Flask app object，否则启动的 CLI 上下文中仍然没有 app 对象
    return dict(app=app)

if __name__ == '__main__':
    manager.run()

