
import requests
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, get_today, t_sleep

from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider

class ZqrbSpider(BaseSpider):


    def __init__(self):
        self.headers = {}
        self.date = self.get_date()
        self.mgr = MogoMgr()
        # self.retry = -1
        # self.retry_flag = -1
        self.failurls = []


    def get_date(self):
        year, month, day = get_today()
        date = str(year) + '-' + str(month) + '-' + str(day)
        return date

    def get_host(self, url):
        host = url.split('/')[2]
        return host

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'epaper.zqrb.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://epaper.zqrb.cn/',
        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url, headers=self.get_news_header(), timeout=3)
        html.encoding = 'utf-8'

        html = etree.HTML(html.text)
        urls = html.xpath('//a[@class="vote_content12px"]/@href')

        new_urls = []
        for ur in urls:
            # log(self.parser_url(ur))
            new_urls.append(self.parser_url(ur))

        # log('数量', len(urls))
        return new_urls


    def parser_url(self, url):
        return self.get_base_url() + url

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
            if news == 'timeout':
                log('访问的新闻超时 暂时跳过')
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

        header = self.get_news_header()

        try:
            html = requests.get(url, headers=header, timeout=3)
            html.encoding = 'utf-8'
        except Exception as e:
            log_line('访问出错')
            self.__class__.retry = 1
            print(e)
            return 'timeout'

        response = etree.HTML(html.text)

        if html.status_code != 200:
            log('访问的URL出错！！！', url)
            return 'error'

        # self.parse_item(response)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        news.spider_name = 'zqrb'
        return news

    def parse_item(self, response):

        try:
            title = response.xpath('//td[@class="h1"]/text()')
            title = ''.join(title).strip()
        except Exception as e:
            title = '未知'

        date = self.date

        try:
            con_list = response.xpath('//div[@id="ozoom"]/descendant-or-self::*/text()')
        except Exception as e:
            con_list = '未知'
        content = ''.join(con_list).strip()
        # log('content', content)
        return title, date, content


    def get_base_url(self):
        year, month, day = get_today()
        year = str(year)
        month = str(month) if month >= 10 else '0' + str(month)
        day = str(day) if day >= 10 else '0' + str(day)

        return 'http://epaper.zqrb.cn/html/{0}-{1}/{2}/'.format(year, month, day)


    def get_start_url(self):
        year, month, day = get_today()
        year = str(year)
        month = str(month) if month >= 10 else '0' + str(month)
        day = str(day) if day >= 10 else '0' + str(day)

        return 'http://epaper.zqrb.cn/html/{0}-{1}/{2}/node_2.htm'.format(year, month, day)

    def run(self):
        log_line('ZqrbSpider 启动！！！')

        url = self.get_start_url()
        urls = self.get_html(url)
        news_list = self.send_request(urls)

        for news in news_list:
            self.mgr.insert(news)

        self.__class__().re_send()

if __name__ == '__main__':
    ZqrbSpider().run()