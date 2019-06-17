#!/usr/bin/env python
# encoding: utf-8


LOG_PATH='./mqtt_client.log'
import logging
# 创建一个logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 创建一个handler，用于写入日志文件
fh = logging.FileHandler(LOG_PATH)
fh.setLevel(logging.INFO)
# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# 定义handler的输出格式
formatter = logging.Formatter('[%(asctime)s][%(filename)s][line: %(lineno)d][%(levelname)s]: %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)
