
import requests
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent
from Tools.log import log_line, log


class Amac2Spider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()
        self.newslist = []
        self.start_urls = [
            'http://www.amac.org.cn/xydt/xyxx/',
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
        items = html.xpath('//div[@class="newsName"]')

        # log_line(len(items))

        for item in items:
            self.parser_item(item)

    def parser_item(self, item):
        news = News()
        news.url = self.parser_url(item.xpath('./a/@href')[0], 'http://www.amac.org.cn')
        news.title = item.xpath('./a/text()')[0]
        news.date = item.getnext().xpath('./text()')[0]

        log(news.url, news.title, news.date)
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
            content = self.parser_data(url)
            self.update_news(url, content)

    def parser_data(self, url):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''

        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'

        response = etree.HTML(html.text)
        log('当前访问的URL', url)

        con_list = response.xpath('//div[@class="ldContent"]/descendant-or-self::*/text()')
        content = ''.join(con_list).strip().replace('\r\n', '')

        log('内容', content)
        return content

    def update_news(self, url, content):
        for news in self.newslist:
            if news.url == url:
                news.content = content

    def run(self):
        log_line('Amac2Spider 启动！！！')

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

if __name__ == '__main__':
    Amac2Spider().run()
