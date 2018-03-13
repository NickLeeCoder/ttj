
import requests
import arrow
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep
from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider


'''
待核实 貌似未完成!!
'''


class Circ2Spider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()
        self.newslist = []
        self.start_urls = [
            'http://www.gov.cn/pushinfo/v150203/base_14px_pubdate.htm',
        ]

    def get_news_header(self):
        return {
            # 'Host': 'www.gov.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.circ.gov.cn/web/site0/tab7642/',

        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''

        t_sleep()
        # log('当前访问的URL', url)

        html = requests.get(url, headers=self.get_news_header(), timeout=3)
        html.encoding = 'utf-8'



        # try:
        #     html = requests.get(url, headers=self.get_news_header(), timeout=3)
        #     html.encoding = 'utf-8'
        # except Exception as e:
        #     log_line('访问出错')
        #     print(e)
        #     self.__class__.retry = 1
        #
        #     return 'timeout'

        # if html.status_code != 200:
        #     return 'error'

        html = etree.HTML(html.text)
        items = html.xpath('//ul[@class="list"]/li')

        # log(len(items))

        for item in items:
            self.parser_item(item)

    def parser_item(self, item):
        url = item.xpath('./a/@href')[0]
        date = item.xpath('./span/text()')[0]

        news = News()
        news.url = self.parser_url(url, 'http://www.gov.cn')
        news.title = item.xpath('./a/text()')[0]
        news.date = date


        # log(news.url, news.title, news.date)

        self.newslist.append(news)

    def parser_url(self, url, base_url):
        if str(url).startswith('http'):
            return url
        else:
            return base_url + url

    def get_newsUrls(self):
        return [news.url for news in self.newslist]


    def run(self):

        log_line('Circ2Spider 启动！！！')

        for url in self.start_urls:
            self.get_html(url)

            for news in self.newslist:
                find_one = self.mgr.find_one('url', news.url)
                if find_one is not None:
                    log_line('该URL已经存在 无需写入')
                    log(news.url)
                    continue
                self.mgr.insert(news)

        self.__class__().re_send()


if __name__ == '__main__':
    Circ2Spider().run()
