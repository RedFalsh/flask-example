#!/usr/bin/env python
# encoding: utf-8

from app import app

if __name__ == '__main__':
    # 注意，这里要关闭自动加载器，不然flask会重启两次，mqtt会有两个客户端，会影响订阅等
    app.run(host='0.0.0.0', port=6000,use_reloader=False, debug=True)
