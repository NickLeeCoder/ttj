
import requests
import json
import arrow
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep

from Tools.log import log_line, log


class CctvSpider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            'Host': 'jingji.cctv.com',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',

        }

    def get_html(self, url):
        '''
        获取顶部 轮播图
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'utf-8'
        # log(html.text)

        html = etree.HTML(html.text)
        urls = html.xpath('//div[@class="shadow"]/ul/li/p/a/@href')
        # log(len(urls), urls)
        return urls


    def get_jsondata(self):
        '''
        直接访问json接口
        :return:
        '''

        url = 'http://jingji.cctv.com/data/index.json'
        html = requests.get(url)
        html.encoding = 'gbk'
        news_list = json.loads(html.text)['rollData']

        urls = []
        for news in news_list:
            urls.append(news['url'])


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
        html = requests.get(url, headers=self.get_news_header())
        html.encoding = 'utf-8'

        response = etree.HTML(html.text)
        log('当前访问的URL', url)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        return news

    def parse_item(self, response):
        try:
            title = response.xpath('//div[@class="cnt_bd"]/h1/text()')[0].strip()
        except Exception as e:

            title = '页面不存在'

        try:
            date = response.xpath('//span[@class="info"]/i/text()')[1].split()[0]
            date = arrow.get(date).format('YYYY-MM-DD')

        except Exception as e:
            try:
                date = response.xpath('//span[@class="info"]/i/text()')[0].split()[1]
                date = arrow.get(date).format('YYYY-MM-DD')
            except Exception as e:
                date = '未知'


        try:
            con_list = response.xpath('//div[@class="cnt_bd"]/p')
            content = self.pasre_content(con_list)
        except Exception as e:
            content = '页面不存在'

        # log(content)
        # log(title, date)

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

        log_line('CctvSpider 启动！！！')

        urls = []
        url = 'http://jingji.cctv.com/'
        urls_1 = self.get_html(url)
        urls_2 = self.get_jsondata()
        urls.extend(urls_1)
        urls.extend(urls_2)

        news_list = self.send_request(urls)

        for news in news_list:
            self.mgr.insert(news)

if __name__ == '__main__':
    CctvSpider().run()
