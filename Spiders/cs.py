
import requests
import re
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep

from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider


class CsSpider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_host(self, url):
        host = url.split('/')[2]
        return host

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            # 'Host': '',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.cs.com.cn/',
        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'gbk'


        # log(html.text)

        pattern = r"\./*[a-z]*/*[a-z]*/[a-z]+/\d+/t\d+_\d+.html"

        urls = re.findall(pattern, html.text)

        new_urls = []
        for ur in  urls:
            new_urls.append(self.parser_url(ur))
        # log(new_urls)

        return new_urls


    def parser_url(self, url):
        log(url)
        return 'http://www.cs.com.cn' + url[1:]

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

            if news == 'error' or news == 'timeout':
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


        # log(html.text)

        response = etree.HTML(html.text)


        if html.status_code != 200:
            log('访问的URL出错！！！', url)
            return 'error'

        # self.parse_item(response)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        news.spider_name = 'cs'

        return news

    def parse_item(self, response):

        try:
            title = response.xpath('//div[@class="artical_t"]/h1/text()')[0].strip()
        except Exception as e:
            title = '未知'
        try:
            date = response.xpath('//span[@class="Ff"]/text()')[0].split()[0]
        except Exception as e:
            date = response.xpath('//span[@class="ctime01"]/text()')[0].split()[0]


        try:
            con_list = response.xpath('//div[@class="artical_c"]/descendant-or-self::*/text()')
        except Exception as e:
            con_list = '未知'

        # contents = [re.sub(r'[a-z]+|\s+', '', cc) for cc in con_list]

        content = ''.join(con_list).strip()
        # log('content', content)
        return title, date, content

    def run(self):
        log_line('CsSpider 启动！！！')

        start_urls = [
            'http://www.cs.com.cn/',
        ]

        for url in  start_urls:
            urls = self.get_html(url)
            news_list = self.send_request(urls)

            for news in news_list:
                self.mgr.insert(news)

        self.__class__().re_send()


if __name__ == '__main__':
    CsSpider().run()
