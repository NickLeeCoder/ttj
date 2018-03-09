
import requests
import arrow
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent
from Tools.log import log_line, log


'''
待核实 貌似未完成!!
'''


class Circ2Spider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()
        self.newslist = []
        self.start_urls = [
            'http://www.gov.cn/pushinfo/v150203/base_14px_pubdate.htm',
        ]

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.gov.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.circ.gov.cn/web/site0/tab7642/',

        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''

        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'

        # log(html.text)

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

    # def send_request(self, urls):
    #
    #     for url in urls:
    #         # 避免重复请求
    #         find_one = self.mgr.find_one('url', url)
    #         if find_one is not None:
    #             log_line('该URL已经存在 无需请求')
    #             log(url)
    #             continue
    #         content = self.get_content(url)
    #         self.update_content(url, content)

    # def get_content(self, url):
    #     '''
    #     请求每一个新闻详情
    #     :param url:
    #     :return:
    #     '''
    #     html = requests.get(url, headers=self.get_news_header())
    #     html.encoding = 'utf-8'
    #
    #     response = etree.HTML(html.text)
    #     log('当前访问的URL', url)
    #
    #     con_list = response.xpath('//span[@id="zoom"]/descendant-or-self::*/text()')
    #     return ''.join(con_list).strip().replace('\r\n', '')

    # def update_content(self, url, content):
    #     for news in self.newslist:
    #         if news.url == url:
    #             news.content = content

    def run(self):

        log_line('Circ2Spider 启动！！！')

        for url in self.start_urls:
            self.get_html(url)
        #     self.send_request(self.get_newsUrls())
        #
        #     # for news in self.newslist:
        #     #     log(news.url, news.content)
        #     #
            for news in self.newslist:
                find_one = self.mgr.find_one('url', news.url)
                if find_one is not None:
                    log_line('该URL已经存在 无需写入')
                    log(news.url)
                    continue
                self.mgr.insert(news)

if __name__ == '__main__':
    Circ2Spider().run()
