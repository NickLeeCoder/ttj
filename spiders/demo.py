
import requests
import json
import arrow
from lxml import etree
from model.news import News
from services.MogoMgr import MogoMgr
from tools.tool import randomUserAgent
from bs4 import BeautifulSoup

from tools.log import log_line, log


class MoHurdSpider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

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
        # html = requests.get(url)
        # html.encoding = 'utf-8'

        # log(html.text)

        # bs = BeautifulSoup(html.text, 'html.parser')
        #
        # urls = bs.find_all('a')
        #
        # new_urls = [url['href'] for url in urls if str(url['href']).startswith('http://www.mohurd.gov.cn/')]

        html = requests.get(url)
        html.encoding = 'utf-8'

        html = etree.HTML(html.text)
        urls = html.xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody')
        log('查找', urls, len(urls))
        # return new_urls


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
        #     news_list.append(news)
        # return news_list


    def get_newsinfo(self, url):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''
        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'

        response = etree.HTML(html.text)
        log('当前访问的URL', url)

        self.parse_item(response)

        # title, date, content = self.parse_item(response)
        # news = News(title=title, date=date, content=content, url=url)
        # return news


    def parse_item(self, response):

        title = response.xpath('//td[@class="tit"]/text()')[0].strip()
        try:
            date = response.xpath('//p[@style="text-align: right"]/text()')[0].strip()
        except Exception as e:
            date = '未知'

        if '摘自' in date:
            log('摘自其他文章', date)
            date = date.split()[2].replace('.', '-')
            log('解析后', date)

        else:
            date = date.split()[0]
            log('解析后', date)

        #
        con_list = response.xpath('//div[@class="union"]/descendant-or-self::*/text()')
        content = ''.join(con_list).strip()

        # return title, date, content


    def run(self):
        url = 'http://www.mohurd.gov.cn/zcjd/index.html'
        urls = self.get_html(url)

        # news_list = self.send_request(urls)
        #
        # for news in news_list:
        #     self.mgr.insert(news)

if __name__ == '__main__':
    MoHurdSpider().run()
