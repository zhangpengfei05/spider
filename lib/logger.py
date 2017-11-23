#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
This module initialize the logger setting.

Modifier: zhangpengfei05(zhangpengfei05@baidu.com)
Date: 2017/10/17
"""

import logging
import logging.handlers
import os

def init_log(module, log_path, level=logging.DEBUG, when="D", backup=7,
              format="%(asctime)s %(filename)s [%(levelname)s] - %(message)s",
              datefmt="%Y-%m-%d %H:%M:%S"):
    """
    init_log - initialize log module

    Args:
      module:       - Module name
      log_path     - Log file path prefix.
                      Log data will go to two files: log_path.log and log_path.log.wf
                      Any non-exist parent directories will be created automatically
      level         - msg above the level will be displayed
                      DEBUG < INFO < WARNING < ERROR < CRITICAL
                      the default value is logging.INFO
      when          - how to split the log file by time interval
                      'S' : Seconds
                      'M' : Minutes
                      'H' : Hours
                      'D' : Days
                      'W' : Week day
                      default value: 'D'
      format        - format of the log
                      default format:
                      %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                      INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
      backup        - how many backup file to keep
                      default value: 7

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """
    formatter = logging.Formatter(format, datefmt)
    logger = logging.getLogger(module)
    logger.setLevel(level)

    pos = log_path.rfind("/")
    log_dir = log_path[:pos]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = logging.handlers.TimedRotatingFileHandler(log_path,
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".wf",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(module):
    """获取logger对象

    Args:
        module: 业务模块名称

    Returns:
        返回logger对象
    """
    log_path = "log/spider.log"
    logger = init_log(module, log_path)
    return logger
