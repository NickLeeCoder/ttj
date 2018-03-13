
import requests
import json
import arrow
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep

from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider


class FangChanSpider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.fangchan.com',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.fangchan.com/policy/28/',
        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = etree.HTML(html.text)
        urls = html.xpath('//ul[@class="related-news-list"]/li/a/@href')

        return urls

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
            html = requests.get(url, headers=self.get_news_header(), timeout=2)
            html.encoding = 'utf-8'
        except Exception as e:
            log_line('访问出错')
            print(e)
            self.__class__.retry = 1

            return 'timeout'



        response = etree.HTML(html.text)


        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        return news


    def parse_item(self, response):

        try:
            title = response.xpath('//div[@class="section top"]/h1/text()')[0].strip()
        except Exception as e:
            title = response.xpath('//h1[@class="clearfix"]/text()')[0].strip()


        try:
            date = response.xpath('/html/body/div[1]/div[2]/div[1]/p/span[2]/text()')[0].split()[0]
        except Exception as e:
            try:
                date = response.xpath('/html/body/div/div[2]/div/div[2]/ul/li[2]/span/text()')[0].split()[0]
            except Exception as e:
                date = '未知'

        con_list = response.xpath('//div[@class="summary-text"]/descendant-or-self::*/text()')
        if len(con_list) == 0:
            con_list = response.xpath('//div[@class="summary_text"]/descendant-or-self::*/text()')

        content = ''.join(con_list).strip()

        return title, date, content


    def run(self):

        log_line('FangChanSpider 启动！！！')


        start_urls = [
            'http://www.fangchan.com/policy/28/',
            'http://www.fangchan.com/plus/nlist.php?tid=2&tags=%E5%8E%9F%E5%88%9B',
            'http://www.fangchan.com/plus/nlist.php?tid=2&column=%E5%AE%8F%E8%A7%82',
            'http://www.fangchan.com/news/6/',
            'http://www.fangchan.com/news/1/',
            'http://www.fangchan.com/news/9/',
            'http://www.fangchan.com/news/5/',
            'http://www.fangchan.com/news/7/',
            'http://www.fangchan.com/news/4/',
        ]

        for url in  start_urls:
            urls = self.get_html(url)
            news_list = self.send_request(urls)

            for news in news_list:
                self.mgr.insert(news)


        self.__class__().re_send()


if __name__ == '__main__':
    FangChanSpider().run()
