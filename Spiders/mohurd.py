
import requests
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep
from Tools.log import log_line, log


class MoHurdSpider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()
        self.newslist = []
        self.start_urls = [
            'http://www.mohurd.gov.cn/zcjd/index.html',
            'http://www.mohurd.gov.cn/fdcy/fdcyzcfb/index.html',
            'http://www.mohurd.gov.cn/fdcy/fdcyxydt/index.html',
            'http://www.mohurd.gov.cn/fdcy/fdcydfxx/index.html',

        ]

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.mohurd.gov.cn',
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
        items = html.xpath('//a[@style="color:#000;;font-size:12px;"]')

        # log_line(len(items))

        for item in items:
            self.parser_item(item)

    def parser_item(self, item):
        news = News()
        news.url = item.xpath('./@href')[0]
        news.title = item.xpath('./text()')[0]
        news.date = item.getparent().getnext().xpath('./text()')[0][1:-1].replace('.', '-').strip()
        self.newslist.append(news)

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
            content = self.get_content(url)
            self.update_content(url, content)

    def get_content(self, url):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''
        t_sleep()
        log('当前访问的URL', url)


        try:
            html = requests.get(url, headers=self.get_news_header(), timeout=2)
            html.encoding = 'utf-8'
        except Exception as e:
            log_line('访问出错')
            print(e)
            return 'timeout'


        response = etree.HTML(html.text)


        con_list = response.xpath('//div[@class="union"]/descendant-or-self::*/text()')
        return ''.join(con_list).strip()

    def update_content(self, url, content):
        for news in self.newslist:
            if news.url == url:
                news.content = content

    def run(self):
        log_line('MoHurdSpider 启动！！！')

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

        if self.retry != -1 and self.retry_flag == -1:
            log_line('部分新闻访问出错 再次进行访问')
            self.retry_flag = 1
            self.run()

if __name__ == '__main__':
    MoHurdSpider().run()
