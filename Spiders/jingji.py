import arrow
import requests
from lxml import etree

from Model.news import News
from Services.MogoMgr import MogoMgr

'''
21经济网
url = 'http://www.21jingji.com/'

'''

'''
    注意新闻详情页 存在多页的情况

    1、是否是多页
    2、如果是多页 且第一页就有关键字 则不需要请求第二页
    '''


class JingJiSpider(object):


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
        news_list = html.xpath('//div[@class="Tlist"]/a/@href')

        return news_list


    def muti_page(self, source, url):
        print(url)
        if url.rsplit('.', 1)[0] + '_' in source:
            # print(url.split('.', -1)[0] + '_')
            print('多页')

    def get_newsinfo(self, newslist):
        '''
        访问每一条新闻详情
        :param newslist: 新闻链接集合
        :return: 新闻model
        '''
        for r in newslist:

            news = requests.get(r)
            news.encoding = 'utf-8'
            response = etree.HTML(news.text)

            item = self.parse_item(response, news.url)
            MogoMgr().insert(item)

    def parse_news(self, html):
        '''
        解析新闻html
        :param html: 新闻详情html
        :return: news Model
        '''
        pass


    def parse_item(self, response, url):
        # 先判断是否为多页新闻 如果是 需要请求下一页
        # global cc
        # cc += 1
        # print(str(cc) + 'hehe')
        # title = (response.xpath('//h2[@class="titl"]/text()').extract())[0].strip()
        title = (response.xpath('//h2[@class="titl"]/text()'))[0].strip()

        date = (response.xpath('//p[@class="Wh"]/span[1]/text()'))[0].strip().split()[0]
        date = str(arrow.get(date)).split('T')[0]

        con_list = response.xpath('//div[@class="detailCont"]/p')
        content = self.pasre_content(con_list)



        item = News()
        item.update = '0'
        item.title = title
        item.date = date
        item.content = content
        item.url = url
        item.spider_name = 'jingji'
        item.is_sended = '0'

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
        news_list = self.get_newslist()
        self.get_newsinfo(news_list)


if __name__ == '__main__':
    JingJiSpider().run()



