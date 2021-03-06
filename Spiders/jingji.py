import arrow
import requests
from lxml import etree
from Tools.log import log_line, log
from Tools.tool import  t_sleep
from Model.news import News
from Services.MogoMgr import MogoMgr
from Spiders.base_spider import BaseSpider

'''
21经济网
url = 'http://www.21jingji.com/'

'''

'''
    注意新闻详情页 存在多页的情况

    1、是否是多页
    2、如果是多页 且第一页就有关键字 则不需要请求第二页
    '''


class JingJiSpider(BaseSpider):


    def get_newslist(self):
        '''
        获取首页的所有新闻链接
        :return: 返回新闻链接集合
        '''

        url = 'http://www.21jingji.com/'

        html = requests.get(url)
        html.encoding = 'utf-8'

        html = etree.HTML(html.text)
        # print(type(html))
        news_list = html.xpath('//a[@class="listTit"]/@href')
        # tt = html.xpath('//a[@class="listTit"]/text()')


        log(len(news_list))


        return news_list


    def muti_page(self, source, url):
        print(url)
        if url.rsplit('.', 1)[0] + '_' in source:
            # print(url.split('.', -1)[0] + '_')
            print('多页')

    def get_newsinfo(self, urls):
        '''
        访问每一条新闻详情
        :param newslist: 新闻链接集合
        :return: 新闻model
        '''
        for url in urls:
            t_sleep()
            log('当前访问的URL', url)


            try:
                html = requests.get(url, timeout=3)
                html.encoding = 'utf-8'
            except Exception as e:
                log_line('访问出错')
                print(e)
                self.__class__.retry = 1

                continue

            if html.status_code != 200:
                continue

            response = etree.HTML(html.text)

            item = self.parse_item(response, html.url)
            MogoMgr().insert(item)

    def parse_news(self, html):
        '''
        解析新闻html
        :param html: 新闻详情html
        :return: news Model
        '''
        pass


    def parse_item(self, response, url):

        try:
            title = (response.xpath('//h2[@class="titl"]/text()'))[0].strip()
        except Exception as e:
            title = '未知'


        try:
            date = (response.xpath('//p[@class="Wh"]/span[1]/text()'))[0].strip().split()[0]
            date = str(arrow.get(date)).split('T')[0]
        except Exception as e:
            date = '未知'


        try:
            con_list = response.xpath('//div[@class="detailCont"]/p')
            content = self.pasre_content(con_list)
        except Exception as e:
            content = '未知'

        item = News()
        item.title = title
        item.date = date
        item.content = content
        item.url = url
        item.spider_name = 'jingji'

        return item


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
        log_line('JingJiSpider 启动！！！')

        news_list = self.get_newslist()
        self.get_newsinfo(news_list)

        # self.__class__().re_send()



if __name__ == '__main__':
    JingJiSpider().run()



