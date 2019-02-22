#!/usr/bin/env python
# encoding: utf-8

from app import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000)

