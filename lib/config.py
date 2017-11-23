#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide config parser service

@author:  zhangpengfei05
@date     2017.10.17
"""

import ConfigParser
import os
import sys

from lib import logger

LOG = logger.get_logger(__name__)

class Config(object):
    """
         读取配置文件

        Attributes:
            cf: ConfigParser对象
            section: 所属配置块名称
        """

    def __init__(self, file_path):
        """Config类构造函数

        Args:
            file_path:  path of the file

        Raises:
            IOError: fail to open log file
        """
        self.cf = ConfigParser.ConfigParser()
        try:
            self.cf.read(file_path)
        except IOError as e:
            LOG.error("Read config file fail, because: %s!" % (str(e)))
            sys.exit(1)

    def get(self, section, key):
        """
            获取配置参数值

        Args:
            section：所属配置块名称
            key: 参数键值

        Returns:
            返回对应参数值

        Raises:
            NoSectionError
            NoOptionError
        """
        val = ""
        try:
            val = self.cf.get(section, key)
        except ConfigParser.NoSectionError:
            LOG.error("No section in conf, section: %s" % section)
            sys.exit(1)
        except ConfigParser.NoOptionError:
            LOG.error("No option in conf, section: %s, option: %s" % (section, key))
            sys.exit(1)
        return val

    def getint(self, section, key):
        """获取int型具体配置参数值

        Args:
            key: 参数键值

        Returns:
            返回int型参数值
        """
        val = 0
        try:
            val = self.cf.getint(section, key)
        except ConfigParser.NoSectionError:
            print "No section in conf, section: %s" % section
        except ConfigParser.NoOptionError:
            print "No option in conf, section: %s, option: %s" % (section, key)
        except ValueError:
            print "Value type is not int, section: %s, option: %s" % (section, key)
        return val
