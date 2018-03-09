
import requests
import arrow
import json
import re
from lxml import etree
from Model.news import News
from Tools.log import log_line, log
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent


class XinHuaSpider():


    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_newlist_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'qc.wa.news.cn',
            'Referer': 'http://www.news.cn/fortune/',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }


    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'www.xinhuanet.com',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }


    def get_caijing_header(self):
        pass
        return {
            'Host': 'www.news.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }


    def get_money(self):
        '''
        金融版面
        :return:
        '''
        url = 'http://www.xinhuanet.com/money/index.htm'
        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'

        html = etree.HTML(html.text)

        urls_all = []

        urls_1 = html.xpath('//li[@class="clearfix"]/h3/a/@href')

        # 只对新闻列表进行处理
        # urls_2 = html.xpath('//li[@class="imp"]/a/@href')
        # urls_3 = html.xpath('//div[@class="swiper-slide"]/a/@href')

        urls_all.extend(urls_1)
        # urls_all.extend(urls_2)
        # urls_all.extend(urls_3)

        # log(len(urls_all), urls_all)

        news_list = []

        for url in urls_all:
            # 避免重复请求
            find_one = self.mgr.find_one('url', url)
            if find_one is not None:
                log_line('该URL已经存在 无需请求')
                log(url)
                continue

            news = self.get_iteminfo(url)
            news_list.append(news)
        return news_list



    def get_lunbo(self):
        '''
        财经版面
        :return:
        '''
        url = 'http://www.news.cn/fortune/'
        html = requests.get(url, headers=self.get_caijing_header())
        html.encoding = 'utf-8'

        html = etree.HTML(html.text)
        urls = html.xpath('//div[@class="swiper-slide"]/a/@href')

        year = arrow.now().date().year

        news_list = []

        for url in urls:
            if str(year)  in url:
                log('需要访问的URL 轮播图', url)
                find_one = self.mgr.find_one('url', url)
                if find_one is not None:
                    log_line('该URL已经存在 无需请求')
                    log(url)
                    continue
                news = self.get_iteminfo(url)
                news_list.append(news)
        return news_list



    def get_itemlist(self, page='1'):
        '''
        获取新华财经 所有新闻详情
        :return: 返回新闻model
        '''

        # 新华财经  -  新闻列表
        url = 'http://qc.wa.news.cn/nodeart/list?nid=11147664&pgnum={0}&cnt=16&tp=1&orderby=1'.format(page)

        html = requests.get(url, headers=self.get_newlist_header())
        items = json.loads(html.text[1:-1])
        items = items['data']['list']

        news_list = []

        for item in items:
            # 避免重复请求
            find_one = self.mgr.find_one('url', item['LinkUrl'])
            if find_one is not None:
                log_line('该URL已经存在 无需请求')
                log(item['LinkUrl'])
                continue

            news = self.get_iteminfo(item['LinkUrl'])
            news_list.append(news)
        return news_list

    def get_iteminfo(self, url):
        '''
        访问每一条新闻详情
        :param itemlist: 新闻链接集合
        :return: 新闻model
        '''
        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'

        response = etree.HTML(html.text)
        title, date, content = self.parse_item(response)

        news = News(title=title, date=date, content=content, url=url)
        return news


    def parse_item(self, response):
        try:
            con_list = response.xpath('//div[@id="p-detail"]/p')
            content = self.pasre_content(con_list)
            title = response.xpath('//div[@class="h-title"]/text()')[0].strip()
            date = response.xpath('//span[@class="h-time"]/text()')[0].split()[0]
        except Exception as e:

            title = '页面不存在'
            date = '页面不存在'
            content = '页面不存在'


        return title, date, content

    def pasre_content(self, con_list):
        '''
        解析正文
        :param response:
        :return:
        '''

        content = ''

        for con in con_list:
            c = con.xpath('./text()')
            if len(c) != 0:
                content = content + c[0].replace(' ', '')

        return content

    def run(self):
        log_line('XinHuaSpider 启动！！！')

        news_list = []
        # 对财经版面的前两页数据进行爬取
        news_list_1 = self.get_itemlist(page='1')
        news_list_2 = self.get_itemlist(page='2')
        news_list_3 = self.get_lunbo()
        news_list_4 = self.get_money()
        news_list.extend(news_list_1)
        news_list.extend(news_list_2)
        news_list.extend(news_list_3)
        news_list.extend(news_list_4)

        for news in news_list:
            self.mgr.insert(news)


if __name__ == '__main__':
    XinHuaSpider().run()


