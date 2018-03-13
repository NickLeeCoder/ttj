
import requests
import re
import arrow
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep

from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider


class CnstockSpider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            # 'Host': '',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.cnstock.com/',
        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'utf-8'

        # log(html.text)

        pattern_1 = r"http://[a-z]+.cnstock.com/[a-z]+,[a-z]+-\d+-\d+.htm"
        pattern_2 = r"http://[a-z]+.cnstock.com/[a-z]+/[a-z]+_[a-z]+/\d+/\d+.htm"
        pattern_3 = r"http://[a-z]+.cnstock.com/[a-z]+/[a-z]+_[a-z]+/[a-z]+_[a-z]+/\d+/\d+.htm"

        # pattern = r'http://[a-z]+.cnstock.com/.*?/\d+.htm'
        # pattern = r'<a href=".*?\d+.htm"'

        # pattern = r'"http://.*?/\d+.htm"'
        # pattern = r'"http://(\.|[a-z]|/|,|-)+\d+.htm"'
        # pattern = r'"http://(\.|[a-z]|/|,|-)*\d+.htm"'


        pattern = '|'.join([pattern_1, pattern_2, pattern_3])
        urls = re.findall(pattern, html.text)
        # for ur in urls:
        #     log(ur)


        # log('数量', len(urls))
        return set(urls)

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

            if news == 'error':
                log('访问的新闻不存在 继续访问下一个URL')
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

        try:
            html = requests.get(url, headers=self.get_news_header(), timeout=2)
            html.encoding = 'gbk'
        except Exception as e:
            log_line('访问出错')
            print(e)
            self.__class__.retry = 1

            return 'timeout'

        # log(html.text)

        response = etree.HTML(html.text)
        log('当前访问的URL', url, html.status_code)

        if html.status_code not in (200, 301, 302):
            log('访问的URL出错！！！', url)
            return 'error'

        # self.parse_item(response)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        return news

    def parse_item(self, response):

        try:
            title = response.xpath('//h1[@class="title"]/text()')
            title = ''.join(title).strip()
        except Exception as e:
            title = '未知'

        try:
            date = response.xpath('//span[@class="timer"]/text()')[0].split()[0]
        except Exception as e:
            date = '未知'
        try:
            con_list = response.xpath('//div[@id="qmt_content_div"]/descendant-or-self::*/text()')
        except Exception as e:
            con_list = ['未知']
        content = ''.join(con_list).strip()
        # log('content', content)
        return title, date, content


    def run(self):
        log_line('CnstockSpider 启动！！！')

        url = 'http://www.cnstock.com/'

        urls = self.get_html(url)

        news_list = self.send_request(urls)

        for news in news_list:
            self.mgr.insert(news)

        self.__class__().re_send()


if __name__ == '__main__':
    CnstockSpider().run()
