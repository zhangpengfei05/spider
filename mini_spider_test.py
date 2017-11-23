#!/usr/bin/env python
#-*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide spider service

@author:  zhangpengfei05(zhangpengfei05@baidu.com)
@date     2017.10.17
"""
import urllib2
import unittest

import mini_spider

from lib import logger
from lib import config
from lib import htmlparse

class TestConfig(unittest.TestCase):
    """test of config load
    """
    def setUp(self):
        """set up for unit test"""
        pass

    def tearDown(self):
        """tear down for unit test"""
        pass

    def test_get(self):
        """test function _get"""
        cfg = config.Config("./conf/spider.conf")
        self.assertEqual(cfg.get("spider", "url_list_file"), "./urls")
        self.assertEqual(cfg.get("spider", "output_directory"), "./output")
        self.assertEqual(cfg.getint("spider", "crawl_interval"), 1)
        self.assertEqual(cfg.getint("spider", "crawl_timeout"), 1)
        self.assertEqual(cfg.get("spider", "target_url"), ".*.(htm|html)$")


class TestLog(unittest.TestCase):
    """
        test  Log
    """
    def setUp(self):
        """set up for unit test"""
        pass

    def tearDown(self):
        """tear down for unit test"""
        pass

    def test_get_logger(self):
        """test function _get_logger"""
        self.assertTrue(logger.get_logger("testlog"))


class TestHtmlparse(unittest.TestCase):
    """
        test htmlparse
    """
    def setUp(self):
        """set up for unit test"""
        self.parser = htmlparse.UrlLister(".*.(htm|html)$")

        self.url = "http://pycm.baidu.com:8081"
        self.crawl_timeout = 1
        self.url_content = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset=utf8>
        <title>Crawl Me</title>
    </head>
    <body>
        <ul>
            <li><a href=page1.html>page 1</a></li>
            <li><a href="page2.html">page 2</a></li>
            <li><a href='page3.html'>page 3</a></li>
            <li><a href='mirror/index.html'>mirror</a></li>
            <li><a href='javascript:location.href="page4.html"'>page 4</a></li>
        </ul>
    </body>
</html>
        """
        self.parse_url = ['http://pycm.baidu.com:8081/mirror/index.html',
                          'http://pycm.baidu.com:8081/page2.html',
                          'http://pycm.baidu.com:8081/page1.html',
                          'http://pycm.baidu.com:8081/page3.html']

        self.result_list = []

    def tearDown(self):
        """tear down for unit test"""
        pass

    def test_get_content(self):
        """test function _get_urls"""

        self.assertEqual(len(self.parser.get_content(self.url, self.crawl_timeout).strip()),
                         len(self.url_content.strip()))

    def test_get_urls(self):
        """test parse"""
        self.rusult_list = self.parser.get_urls(self.url_content, self.url)
        self.assertEqual(self.parse_url.sort(), self.result_list.sort())


class TestSpider(unittest.TestCase):
    """
        test spider
    """
    def setUp(self):
        """set up for unit test"""
        self.spider = mini_spider.Spider('./conf/spider.conf')
        self.url = set(["http://pycm.baidu.com:8081/"])

    def tearDown(self):
        """tear down for unit test"""
        pass

    def test_seedfile_load(self):
        """test function _seedfile_load"""
        self.spider._seedfile_load()
        self.assertEqual(self.spider.handled_set, self.url)

if __name__ == "__main__":
    unittest.main()
