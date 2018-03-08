
import requests
import re
import arrow
from lxml import etree
from model.news import News
from services.MogoMgr import MogoMgr
from tools.tool import randomUserAgent, get_today

from tools.log import log_line, log


class StcnSpider():

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()


    # def get_date(self):
    #     year, month, day = get_today()
    #     date = str(year) + '-' + str(month) + '-' + str(day)
    #     return date

    def get_host(self, url):
        host = url.split('/')[2]
        return host

    def get_news_header(self):
        '''
        请求新闻列表的请求头与请求新闻详情的请求头不一样
        :return:
        '''
        return {
            # 'Host': 'epaper.zqrb.cn',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.stcn.com/',
        }


    def get_html(self, url):
        '''
        :param url:
        :return:
        '''
        html = requests.get(url)
        html.encoding = 'gbk'

        # log(html.text)

        pattern = r"http://[a-z]+\.stcn.com/\d+/\d+/\d+.shtml"

        urls = re.findall(pattern, html.text)

        # new_urls = []
        # for ur in urls:
        #     log(ur)
            # new_urls.append(self.parser_url(ur))

        log('数量', len(urls))
        return urls


    # def parser_url(self, url):
    #     return self.get_base_url() + url

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

            news_list.append(news)
        return news_list


    def get_newsinfo(self, url):
        '''
        请求每一个新闻详情
        :param url:
        :return:
        '''
        header = self.get_news_header()
        html = requests.get(url, headers=header)
        html.encoding = 'utf-8'

        # log(html.text)

        response = etree.HTML(html.text)
        log('当前访问的URL', url, html.status_code)

        if html.status_code not in (200, 301, 302):
            log('访问的URL出错！！！', url)
            return 'error'

        # self.parse_item(response)

        title, date, content = self.parse_item(response)
        news = News(title=title, date=date, content=content, url=url)
        return news

    def parse_item(self, response):

        try:
            title = response.xpath('//div[@class="intal_tit"]/h2/text()')
            title = ''.join(title).strip()
        except Exception as e:
            title = '未知'

        try:
            date = response.xpath('//div[@class="info"]/text()')[0].split()[0]
        except Exception as e:
            date = '未知'
        try:
            con_list = response.xpath('//div[@id="ctrlfscont"]/descendant-or-self::*/text()')
        except Exception as e:
            con_list = ['未知']
        content = ''.join(con_list).strip()
        # log('content', content)
        return title, date, content


    # def get_base_url(self):
    #     year, month, day = get_today()
    #     year = str(year)
    #     month = str(month) if month >= 10 else '0' + str(month)
    #     day = str(day) if day >= 10 else '0' + str(day)
    #
    #     return 'http://epaper.zqrb.cn/html/{0}-{1}/{2}/'.format(year, month, day)


    def run(self):
        url = 'http://www.stcn.com/'

        urls = self.get_html(url)
        news_list = self.send_request(urls)

        for news in news_list:
            self.mgr.insert(news)

if __name__ == '__main__':
    StcnSpider().run()
