opyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide spider service

@author:  zhangpengfei05(zhangpengfei05@baidu.com)
@date     2017.10.17
"""
import argparse
import chardet
import getopt
import os
import Queue as queue
import re
import StringIO as stringio
import sgmllib
import sys
import threading
import time
import urllib
import urllib2
import urlparse

from lib import htmlparse
from lib import config
from lib import logger

LOG = logger.get_logger(__name__)

class Spider(object):
    """
         Spider主程序

        Attributes:
            module_name: 业务模块名称
            cfg: 配置文件解析类对象
            url_queue: 待抓取的url队列，包括url和当前抓取深度
            handled_set: 已处理过的url的set集合，抓取操作完成后将url加入
            lock: 线程锁
            fetch: 具体抓取操作执行函数
            max_depth: 最大抓取深度(种子为0级)
            crawl_interval: 抓取间隔. 单位: 秒
            crawl_timeout: 抓取超时. 单位: 秒
            thread_count: 抓取的线程数量
            target_url: 需要存储的目标网页URL pattern(正则表达式)
        """
    def __init__(self, config_file):

        self.conf_file = config_file
        self.cfg = config.Config(config_file)
        self.module_name = 'spider'
        self.max_depth = self.cfg.getint(self.module_name, 'max_depth')
        self.crawl_interval = self.cfg.getint(self.module_name, 'crawl_interval')
        self.crawl_timeout = self.cfg.getint(self.module_name, 'crawl_timeout')
        self.target_url = self.cfg.get(self.module_name, 'target_url')
        self.output_directory = self.cfg.get(self.module_name, 'output_directory')
        self.url_list_file = self.cfg.get(self.module_name, 'url_list_file')
        self.thread_count = self.cfg.getint(self.module_name, 'thread_count')

        self.target_pattern = re.compile(self.target_url)

        self.url_queue= queue.Queue()
        self.handled_set = set()
        self.lock = threading.Lock()

    def _save_url(self, url):
        """
           保存网页内容，并把url中的"/"替换为"_"
        """
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        save_name=os.path.join(self.output_directory, url.replace('/', '_'))
        try:
            urllib.urlretrieve(url, save_name)
            LOG.info("saving %s success." % url)
        except IOError as err:
            LOG.error("saving %s error. error message: %s" % (url, err))

    def _seedfile_load(self):
        """
            获取种子文件, 加入url_queue和handled_set
        """
        try:
            file_path = os.path.split(self.conf_file)
            url_list_file = os.path.join(file_path[0], self.url_list_file.split('/')[1])
            with open(url_list_file) as file:
                for url in file:
                    seed_url = url.strip('\r\n')
                    self.url_queue.put_nowait((seed_url, 0))
                    #set保证加入url_queue的唯一性
                    self.handled_set.add(seed_url)
                    LOG.debug("add seed url to queue: %s" % seed_url)
        except IOError:
            LOG.error("load seedfile error.")

    def _fetch(self, index):
        """
           线程抓取操作
           从url_queue中取出url

        Args:
            index: thread编号
        """

        #调用网页解析类：htmlparse.UrlLister
        parser = htmlparse.UrlLister(self.target_url)
        while True:
            queue_empty = False
            try:
                # 获取待抓取url和当前抓取深度
                url, depth = self.url_queue.get_nowait()

                #获取网页内容
                content = parser.get_content(url, self.crawl_timeout)

                LOG.info("thread-%s fetch completed: %s" % (index, url))
                if content:
                    # 判断是否到最大深度，决定是否获取下一级的url
                    if depth < self.max_depth:
                        urls = parser.get_urls(content, url)
                        next_depth = depth + 1
                        for next_url in urls:
                            with self.lock:
                                # 仅将没有处理过的url加入到待抓取队列
                                if next_url not in self.handled_set:
                                    self.url_queue.put((next_url, next_depth))

                                    # 加入到已处理url列表中，保证同一个url只进入待抓取队列一次
                                    self.handled_set.add(next_url)
                                    LOG.debug("thread-%s add url to queue: %s" % (index, next_url))

                #保存网页内容
                self._save_url(url)

            except queue.Empty:
                LOG.info("url queue now is empty, thread-%s start sleep" % (index))
                queue_empty = True
            except sgmllib.SGMLParseError as e:
                LOG.warning("thread-%s parse exception, url: %s, msg: %s"
                          % (index, url, e))
            except Exception as e:
                LOG.warning("thread-%s parse error, url: %s, msg: %s"
                            % (index, url, e))
            finally:
                if not queue_empty:
                    self.url_queue.task_done()
                time.sleep(self.crawl_interval)

    def crawl(self):
        """
           抓取主函数
        return:
            None
        """
        self._seedfile_load()
        LOG.info("Spider start to crawl urls!")

        for x in xrange(self.thread_count):
            thread = threading.Thread(target=self._fetch, args=(x,))
            thread.setDaemon(True)
            thread.start()

        self.url_queue.join()
        LOG.info("Spider end crawling.")


def main():
    """
        main 函数
    """
    VERSION = "1.0"

    parser = argparse.ArgumentParser(prog='spider')
    parser.add_argument("-c", "--conf", help="config file path", required=True)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
    args = parser.parse_args()

    spider = Spider(args.conf)
    spider.crawl()

if __name__ == "__main__":
    main()
