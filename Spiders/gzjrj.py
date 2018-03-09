
import requests
import json
import arrow
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent

from Tools.log import log_line, log

'''
暂未完成  所有新闻详情为图片 后续完成

可考虑修改为 仅适用标题进行 关键字 检索

'''


class GzjrjSpider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.shanghai.gov.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = etree.HTML(html.text)
        urls = html.xpath('//div[@class="mainContent"]/ul/li/a/@href')
        log('提取的URL', urls)

        return self.parser_url(urls)


    def parser_url(self, urls):
        base_url = 'http://www.gzjr.gov.cn/'
        new_urls = []
        for url in urls:
            if str(url).endswith('.pdf'):
                continue

            url = base_url + url.split('../../')[1]
            log('拼接后的url', url)
            new_urls.append(url)
        return new_urls


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
        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'gbk'

        response = etree.HTML(html.text)
        log('当前访问的URL', url)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        return news


    def parse_item(self, response):

        title = response.xpath('//div[@id="ivs_title"]/text()')[0].strip()
        date = response.xpath('//div[@id="ivs_date"]/text()')[0][1:-1].strip()
        date = arrow.get(date).format('YYYY-MM-DD')

        con_list = response.xpath('//div[@id="ivs_content"]/descendant-or-self::*/text()')
        content = ''.join(con_list).strip()

        return title, date, content


    def run(self):
        url = 'http://www.gzjr.gov.cn/gzjr/zchgh/list.shtml'
        urls = self.get_html(url)

        # news_list = self.send_request(urls)
        #
        # for news in news_list:
        #     self.mgr.insert(news)

if __name__ == '__main__':
    GzjrjSpider().run()
