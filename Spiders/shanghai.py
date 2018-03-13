
import requests
import json
import arrow
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep

from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider


class ShangHaiSpider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.shanghai.gov.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = etree.HTML(html.text)
        urls = html.xpath('//ul[@class="uli14 pageList"]/li/a/@href')

        return self.parser_url(urls)


    def parser_url(self, urls):
        base_url = 'http://www.shanghai.gov.cn'
        new_urls = []
        for url in urls:
            if str(url).endswith('.pdf'):
                continue

            url = base_url + url
            new_urls.append(url)
        return new_urls


    def send_request(self, urls):
        news_list = []
        for url in urls:
            # 避免重复请求
            find_one = self.mgr.find_one('url', url)
            if find_one is not None:
                log_line('该URL已经存在 无需请求')
                log(url)
                continue
            news = self.get_newsinfo(url)
            if news == 'timeout' or news == 'error':
                continue
            news_list.append(news)
        return news_list


    def get_newsinfo(self, url):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''
        t_sleep()
        log('当前访问的URL', url)


        try:
            html = requests.get(url, headers=self.get_news_header(), timeout=3)
            html.encoding = 'gbk'
        except Exception as e:
            log_line('访问出错')
            print(e)
            self.__class__.retry = 1

            return 'timeout'

        if html.status_code != 200:
            log('访问的URL出错！！！', url)
            return 'error'

        response = etree.HTML(html.text)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        news.spider_name = 'shanghai'
        return news


    def parse_item(self, response):

        title = response.xpath('//div[@id="ivs_title"]/text()')[0].strip()
        date = response.xpath('//div[@id="ivs_date"]/text()')[0][1:-1].strip()
        date = arrow.get(date).format('YYYY-MM-DD')

        con_list = response.xpath('//div[@id="ivs_content"]/descendant-or-self::*/text()')
        content = ''.join(con_list).strip()

        return title, date, content


    def run(self):
        log_line('ShangHaiSpider 启动！！！')

        url = 'http://www.shanghai.gov.cn/nw2/nw2314/nw2319/nw41893/index.html'
        urls = self.get_html(url)

        news_list = self.send_request(urls)

        for news in news_list:
            self.mgr.insert(news)

        self.__class__().re_send()


if __name__ == '__main__':
    ShangHaiSpider().run()
