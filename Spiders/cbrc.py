
import requests
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent
from Tools.log import log_line, log


class CbrcSpider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()
        self.newslist = []
        self.start_url = 'http://www.cbrc.gov.cn/chinese/zhengcefg.html'


    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.cbrc.gov.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }

    def get_html(self, url):
        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'
        html = etree.HTML(html.text)
        items = html.xpath('//a[@class="STYLE8"]')


        for item in items:
            news = News()
            news.url = item.xpath('./@href')[0]
            news.title = item.xpath('./@title')[0]
            news.date = item.getparent().getnext().xpath('./text()')[0].strip()

            self.newslist.append(news)

        return self.parser_url(self.newslist)

    def parser_url(self, newslist):
        base_url = 'http://www.cbrc.gov.cn'
        new_urls = []
        for news in newslist:
            url = base_url + news.url
            news.url = url
            # log('拼接后的URL', url)
            new_urls.append(url)
        return new_urls



    def send_request(self, urls):
        for url in urls:
            # 避免重复请求
            find_one = self.mgr.find_one('url', url)
            if find_one is not None:
                log_line('该URL已经存在 无需请求')
                log(url)
                continue

            content = self.get_content(url)
            for news in self.newslist:
                if news.url == url:
                    news.content = content


    def get_content(self, url):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''
        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'

        response = etree.HTML(html.text)
        log('当前访问的URL', url)
        return self.parse_item(response)

    def parse_item(self, response):

        try:
            con_list = response.xpath('//div[@class="notice_t"]/descendant-or-self::*/text()')
            content = ''.join(con_list).strip().replace('\r\n', '')
        except Exception as e:
            content = '页面不存在'
        return content

    def run(self):
        log_line('CbrcSpider 启动！！！')

        urls = self.get_html(self.start_url)
        self.send_request(urls)

        for news in self.newslist:
            find_one = self.mgr.find_one('url', news.url)
            if find_one is not None:
                log_line('该URL已经存在 无需写入')
                log(news.url)
                continue
            self.mgr.insert(news)

if __name__ == '__main__':
    CbrcSpider().run()
