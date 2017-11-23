#!/usr/bin/env python
#-*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide webpage parser service

@author:  zhangpengfei05(zhangpengfei05@baidu.com)
@date     2017.10.17
"""

import chardet
import re
import sgmllib
import urllib
import urllib2
import urlparse

from lib import logger

LOG = logger.get_logger(__name__)

class UrlLister(sgmllib.SGMLParser):
    """获取网页中所有链接地址,加入到列表中"""

    def __init__(self, target_url):
        self.target_url = target_url
        self.target_pattern = re.compile(self.target_url)

    def reset(self):
        self.urls = []
        sgmllib.SGMLParser.reset(self)

    def start_a(self, attrs):
        """在序列中取出tag为a的URL地址"""
        urlList = [v for k, v in attrs if k == 'href']
        if urlList:
            self.urls.extend(urlList)

    def get_content(self, url, crawl_timeout):
        """
            抓取网页内容根据url获取网页的内容

        Args:
            url: 抓取的url
            crawl_timeout: 抓取url超时时间

        Returns:
            content：网页内容
        """
        content = ""
        response = None
        try:
            response = urllib2.urlopen(url, timeout=crawl_timeout)
            content = response.read()
        except ValueError as e:
            LOG.error("Request value error, url: %s, reason: %s" % (url, e))
        except urllib2.URLError as e:
            LOG.error("Url error, url: %s, reason: %s" % (url, e))
        finally:
            if response is not None:
                response.close()
        return content

    def get_urls(self, url_content, url):
        """
            获取网页中超链接的URL地址后处理返回

        Args:
            url_content: url网页内容
            url: 解析的url

        Returns:
            urlList：url中符合条件的url列表
        """
        urlList = []
        char_dict = chardet.detect(url_content)
        web_encoding = char_dict['encoding']
        if web_encoding == 'utf-8' or web_encoding == 'UTF-8':
            content = url_content
        else:
            try:
                content = url_content.decode('GBK', 'ignore').encode('utf-8')
            except UnicodeDecodeError as err:
                LOG.error("Decode url error. because: %s.", err)
                return None
        if len(content) == 0:
            return urlList

        self.reset()
        # 装填分析器，使得"start_"开头的方法都被执行,并自动匹配出所有已定义的start_方法的tag信息
        self.feed(content)

        urlList = self.urls
        urlTup = urlparse.urlparse(url)  # 解析URL
        rootUrl = urlTup.scheme + "://" + urlTup.netloc + urlTup.path

        #去除javascript开头或不符合正则的url
        for v in urlList:
            if v.startswith("javascript:") or not re.match(self.target_pattern, v):
                urlList.remove(v)

        #拼接解析的url
        for i in range(len(urlList)):
            fullUrl = urlparse.urljoin(rootUrl, urlList[i])
            urlList[i] = fullUrl

        return urlList
