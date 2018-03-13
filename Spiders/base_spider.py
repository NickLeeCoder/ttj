
import requests
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep
from Tools.log import log_line, log


class BaseSpider():
    retry = -1
    retry_flag = -1

    def run(self):
        pass

    @classmethod
    def re_send(cls):

        if cls.retry != -1 and cls.retry_flag == -1:
            log_line('部分新闻访问出错 再次进行访问')
            log('再次运行的爬虫类型', cls)
            cls.retry_flag = 1
            cls().run()




