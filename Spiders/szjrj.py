
import requests
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep
from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider


class SzJrjSpider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_news_header_fg(self):
        '''
        政策法规
        :return:
        '''
        return {
            'Host': 'www.jr.sz.gov.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.jr.sz.gov.cn/sjrb/xxgk/zcfg/jrfz/',
        }

    def base_url_fg(self):
        '''
        政策法规URL
        :return:
        '''
        return 'http://www.jr.sz.gov.cn/sjrb/xxgk/zcfg/jrfz'

    def get_news_header_gh(self):
        '''
        规划计划
        :return:
        '''
        return {
            'Host': 'www.jr.sz.gov.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.jr.sz.gov.cn/sjrb/xxgk/sjtj/zxtjxx/',
        }

    def base_url_gh(self):
        '''
        规划计划URL
        :return:
        '''
        return 'http://www.jr.sz.gov.cn/sjrb/xxgk/sjtj/zxtjxx'


    def get_html(self, url, base_url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'utf-8'
        html = etree.HTML(html.text)
        urls = html.xpath('//li[@class="clearfix"]/a/@href')
        return self.parser_url(urls, base_url)


    def parser_url(self, urls, base_url):
        new_urls = []
        for url in urls:
            if str(url).endswith('.pdf'):
                continue

            url = base_url + url[1:]
            new_urls.append(url)
        return new_urls


    def send_request(self, urls, headers):
        news_list = []
        for url in urls:
            # 避免重复请求
            find_one = self.mgr.find_one('url', url)
            if find_one is not None:
                log_line('该URL已经存在 无需请求')
                log(url)
                continue

            news = self.get_newsinfo(url, headers)

            if news == 'timeout' or news == 'error':
                continue
            news_list.append(news)
        return news_list


    def get_newsinfo(self, url, headers):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''
        t_sleep()
        log('当前访问的URL', url)


        try:
            html = requests.get(url, headers=headers, timeout=3)
            html.encoding = 'utf-8'
        except Exception as e:
            log_line('访问出错')
            print(e)
            self.__class__.retry = 1
            return 'timeout'

        if html.status_code != 200:
            log('访问的URL出错！！！', url)
            return 'error'

        response = etree.HTML(html.text)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        news.spider_name = 'szjrj'
        return news


    def parse_item(self, response):

        title = response.xpath('//div[@class="coninside cc"]/h1/text()')[0].strip()
        date = response.xpath('//div[@class="coninfo"]/text()')[0].split()[0]
        con_list = response.xpath('//div[@class="TRS_Editor"]/descendant-or-self::*/text()')
        content = ''.join(con_list).strip()

        return title, date, content



    def run(self):
        log_line('SzJrjSpider 启动！！！')

        news_list = []

        url_gh = 'http://www.jr.sz.gov.cn/sjrb/xxgk/sjtj/zxtjxx/'
        urls_gh = self.get_html(url_gh, self.base_url_gh())

        url_fg = 'http://www.jr.sz.gov.cn/sjrb/xxgk/zcfg/jrfz/'
        urls_fg = self.get_html(url_fg, self.base_url_fg())

        news_list_fg = self.send_request(urls_fg, self.get_news_header_fg())
        news_list_gh = self.send_request(urls_gh, self.get_news_header_gh())

        news_list.extend(news_list_fg)
        news_list.extend(news_list_gh)

        for news in news_list:
            self.mgr.insert(news)

        self.__class__().re_send()


if __name__ == '__main__':
    SzJrjSpider().run()
