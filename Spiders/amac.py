
import requests
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep
from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider


class AmacSpider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()
        self.newslist = []
        self.retry = -1
        self.retry_flag = -1
        self.failurls = []
        self.start_urls = [
            'http://www.amac.org.cn/flfg/flfgwb/',


        ]

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.amac.org.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''

        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'
        html = etree.HTML(html.text)
        items = html.xpath('//div[@class="newsTrTitle"]/a')

        # log_line(len(items))

        for item in items:
            self.parser_item(item)

    def parser_item(self, item):
        news = News()
        news.spider_name = 'amac'
        news.url = self.parser_url(item.xpath('./@href')[0], 'http://www.amac.org.cn')
        news.title = item.xpath('./text()')[0]

        self.newslist.append(news)


    def parser_url(self, url, base_url):
        return base_url + url.split('../..')[1]

    def get_newsUrls(self):
        return [news.url for news in self.newslist]

    def send_request(self, urls):

        for url in urls:
            # 避免重复请求
            find_one = self.mgr.find_one('url', url)
            if find_one is not None:
                log_line('该URL已经存在 无需请求')
                log(url)
                continue
            date, content = self.parser_data(url)
            if content in ('error', 'timeout'):
                continue
            self.update_news(url, content, date)

    def parser_data(self, url):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''
        t_sleep()
        log('当前访问的URL', url)

        try:
            html = requests.get(url, headers=self.get_news_header(), timeout=3)
            html.encoding = 'utf-8'
        except Exception as e:
            log_line('访问出错')
            print(e)
            self.__class__.retry = 1
            return 'timeout', 'timeout'

        if html.status_code != 200:
            return 'error', 'error'

        response = etree.HTML(html.text)

        con_list = response.xpath('//div[@class="ldContent"]/descendant-or-self::*/text()')
        content = ''.join(con_list).strip()

        date = response.xpath('//div[@class="ldDate"]/text()')[0]
        date = date.split('：')[1]
        # log('内容', content)
        return date, content

    def update_news(self, url, content, date):
        for news in self.newslist:
            if news.url == url:
                news.content = content
                news.date = date

    def run(self):
        log_line('AmacSpider 启动！！！')

        for url in self.start_urls:
            self.get_html(url)
            self.send_request(self.get_newsUrls())

            for news in self.newslist:
                find_one = self.mgr.find_one('url', news.url)
                if find_one is not None:
                    log_line('该URL已经存在 无需写入')
                    log(news.url)
                    continue
                self.mgr.insert(news)

        self.__class__().re_send()


if __name__ == '__main__':
    AmacSpider().run()

