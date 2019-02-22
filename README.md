# flask-example
一个机遇flask的项目基本设计框架

# 项目目录结构：
```
config.py
requirements.txt
runserver.py
config.py
manager.py
app/
    __init__.py
    admin/__init__.py
    views/index.py
    models.py
    forms.py
    static/
    templates/
    
    ```
    
    
    
# 需要：
  1、以及安装好mysql数据库，并添加test数据库
  2、python版本在3.0以上
  
# 安装

1. git下载

`git clone`

2. 进入项目目录

`cd flask-example`

3. 安装依赖包

`pip install -r requirement.txt`

4、初始化数据库表格

`python manager.py db init`
`python manager.py db migrate`
`python manager.py db upgrade`

5、运行

`python runserver.py`

# 项目中添加了后台管理flask-admin
浏览器访问：`localhost:5000/admin` 即可看到后台管理界面
