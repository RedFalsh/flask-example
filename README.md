# flask-example
一个flask的项目基本设计框架, 可快速部署flask项目

# 项目包含

## - 项目蓝图管理：`flask-blueprint`

参考：http://flask.pocoo.org/docs/1.0/tutorial/blog/

- manager运行项目和数据库初始化管理：`flask-script`

参考: https://github.com/smurfix/flask-script

- 后台管理插件: `flask-admin`

参考: https://github.com/flask-admin/flask-admin


# 项目目录结构：

``` python

config.py             # 配置文件
requirements.txt      # 依赖包
runserver.py          # app运行脚本
manager.py            # manager管理数据库
app/
    __init__.py       # app初始化
    admin/__init__.py # admin后台管理
    views/index.py    # 视图文件夹
    models.py         # 数据库model
    forms.py          # 表格
    static/           # 静态文件css, js
    templates/        # 网页html文件

```



# 需要：
  1、以及安装好mysql数据库，并添加test数据库
  2、python版本在3.0以上

# 安装

1. git下载

`git clone https://github.com/RedFalsh/flask-example.git`

2. 进入项目目录

`cd flask-example`

3. 安装依赖包, 建议在python虚拟机下安装

参考：https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432712108300322c61f256c74803b43bfd65c6f8d0d0000

`pip install -r requirement.txt`

4、初始化数据库表格

`python manager.py db init`

`python manager.py db migrate`

`python manager.py db upgrade`

5、运行

`python runserver.py`

