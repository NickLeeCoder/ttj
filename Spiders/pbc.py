
import requests
import re
import arrow
import jsbeautifier
import js2py
from lxml import etree
from Model.news import News
from Services.MogoMgr import MogoMgr
from Tools.tool import randomUserAgent, t_sleep

from Tools.log import log_line, log
from Spiders.base_spider import BaseSpider



'''
目前思路比较混乱  需要好好整理一下再写
主要是需要更换解析的思路？？？？？
'''



class PbcSpider(BaseSpider):

    def __init__(self):
        self.headers = {}
        self.mgr = MogoMgr()
        self.host_url = 'http://www.pbc.gov.cn'


    def get_news_header(self):
        return {
            # 'Host': '',
            'User-Agent': randomUserAgent(),
            'Pragma': 'no-cache',
            'Referer': 'http://www.cnstock.com/',
        }



    def get_html(self, dest_url):
        '''
        解码PBC的JavaScript脚本 并再次访问获取原始HTML
        :param url: 需要访问的PBC链接
        :return: HTML源码  requests中的 response 类型
        '''



        r = requests.session()



        # dest_url = 'http://www.pbc.gov.cn/rmyh/105208/index.html'
        # dest_url = 'http://www.pbc.gov.cn/tiaofasi/144941/index.html'
        # dest_url = 'http://www.pbc.gov.cn/rmyh/105145/index.html'
        # dest_url = 'http://www.pbc.gov.cn/jinrongshichangsi/147160/147289/index.html'


        # 利用session保存cookie信息，第一次请求会设置cookie类似{'wzwsconfirm': 'ab3039756ba3ee041f7e68f634d28882', 'wzwsvtime': '1488938461'}，与js解析得到的cookie合起来才能通过验证
        # r = requests.session()
        content = r.get(dest_url).content
        # 获取页面脚本内容
        re_script = re.search(r'<script type="text/javascript">(?P<script>.*)</script>', content.decode('utf-8'),
                              flags=re.DOTALL)
        # 用点匹配所有字符，用(?P<name>...)获取：https://docs.python.org/3/howto/regex.html#regex-howto
        # cheatsheet：https://github.com/tartley/python-regex-cheatsheet/blob/master/cheatsheet.rst
        script = re_script.group('script')
        script = script.replace('\r\n', '')
        # 在美化之前，去掉\r\n之类的字符才有更好的效果
        res = jsbeautifier.beautify(script)
        # 美化并一定程度解析js代码：https://github.com/beautify-web/js-beautify
        with open('x.js', 'w') as f:
            f.write(res)
        # 写入文档进行查看分析

        jscode_list = res.split('function')
        var_ = jscode_list[0]
        var_list = var_.split('\n')
        template_js = var_list[3]  # 依顺序获取，亦可用正则
        template_py = js2py.eval_js(template_js)
        # 将所有全局变量插入第一个函数变为局部变量并计算
        function1_js = 'function' + jscode_list[1]
        position = function1_js.index('{') + 1
        function1_js = function1_js[:position] + var_ + function1_js[position:]
        function1_py = js2py.eval_js(function1_js)
        cookie1 = function1_py(str(template_py))  # 结果类似'NA=='
        # 保存得到的第一个cookie
        cookies = {}
        cookies['wzwstemplate'] = cookie1
        # 对第三个函数做类似操作
        function3_js = 'function' + jscode_list[3]
        position = function3_js.index('{') + 1
        function3_js = function3_js[:position] + var_ + function3_js[position:]
        function3_py = js2py.eval_js(function3_js)
        middle_var = function3_py()  # 是一个str变量，结果类似'WZWS_CONFIRM_PREFIX_LABEL4132209'
        cookie2 = function1_py(middle_var)
        cookies['wzwschallenge'] = cookie2
        # 关于js代码中的document.cookie参见 https://developer.mozilla.org/zh-CN/docs/Web/API/Document/cookie
        dynamicurl = js2py.eval_js(var_list[0])

        # 利用新的cookie对提供的动态网址进行访问即是我们要达到的内容页面了
        r.cookies.update(cookies)
        # content = r.get(self.host_url + dynamicurl).content.decode('utf-8')


        try:
            content = r.get(self.host_url + dynamicurl, timeout=3)
            content.encoding = 'utf-8'
        except Exception as e:
            log_line('访问出错')
            print(e)
            self.__class__.retry = 1

            return 'timeout'

        return content

    def send_request(self, urls, parser_item_fuc):
        '''
        用于请求每一个具体的新闻链接
        :param urls:   具体新闻URL
        :param parser_item_fuc: 用于解析每一个新闻详情的函数
        :return: 返回解析好的News类型列表
        '''
        news_list = []
        for url in urls:
            # 避免重复请求
            find_one = self.mgr.find_one('url', url)
            if find_one is not None:
                log_line('该URL已经存在 无需请求')
                log(url)
                continue

            news = self.get_newsinfo(url, parser_item_fuc)

            if news == 'error' or news == 'timeout':
                continue

            news_list.append(news)
        return news_list


    def get_newsinfo(self, url, parser_item_fuc):
        '''
        请求每一个新闻详情
        '''
        t_sleep()

        log('当前访问的URL', url)


        html = self.get_html(url)
        if html == 'timeout':
            return 'error'

        response = etree.HTML(html.text)
        log('当前访问的URL', url, html.status_code)

        if html.status_code != 200:
            log('访问的URL出错！！！', url)
            return 'error'

        # parser_item_fuc(response)

        title, date, content = parser_item_fuc(response)
        news = News(title=title, date=date, content=content, url=url)
        news.spider_name = 'pbc'
        return news



    def parser_gonggao_list(self, content):
        '''
        公告信息页面的解析
        :param content: 公告信息页的HTML源码 用于提取公告信息
        :return: 返回的是公告信息详情链接
        '''
        html = etree.HTML(content.text)
        doms = html.xpath('//font[@class="newslist_style"]')

        urls = []

        for e in doms:
            # log('标题', e.xpath('./a/text()')[0].strip())
            # log('url', e.xpath('./a/@href')[0].strip())
            # log('日期', e.getnext().xpath('./text()')[0].strip())
            url = self.host_url + e.xpath('./a/@href')[0].strip()

            urls.append(url)
        return urls


    def parser_falvfagui(self, content):
        html = etree.HTML(content.text)
        doms = html.xpath('//td[@class="font14 bgdian"]')

        urls = []

        for e in doms:

            url = self.host_url + e.xpath('./a/@href')[0].strip()
            # log('标题', e.xpath('./a/text()')[0].strip())

            # log('解析的新闻URL', url)

            urls.append(url)
        return urls


    def parser_huobi(self, content):
        html = etree.HTML(content.text)
        doms = html.xpath('//a[@class="hei12jj"]')

        urls = []

        for e in doms:

            url = self.host_url + e.xpath('./@href')[0].strip()
            # log('标题', e.xpath('./a/text()')[0].strip())

            # log('解析的新闻URL', url)

            urls.append(url)
        return urls


    def parser_xindai(self, content):
        html = etree.HTML(content.text)
        doms = html.xpath('//a[@class="hei12jj"]')

        urls = []

        for e in doms:

            url = self.host_url + e.xpath('./@href')[0].strip()
            # log('标题', e.xpath('./text()')[0].strip())

            # log('解析的新闻URL', url)

            urls.append(url)
        return urls


    def parse_gonggao_item(self, response):
        '''
        解析公告信息详情
        :param response:
        :return:
        '''
        try:
            title = response.xpath('//h2[@style="FONT-SIZE: 16px"]/text()')
            title = ''.join(title).strip()
        except Exception as e:
            title = '未知'

        try:
            date = response.xpath('//td[@class="hui12"][@align="right"]/text()')[0]
        except Exception as e:
            date = '未知'
        try:
            con_list = response.xpath('//font[@id="zoom"]/descendant-or-self::*/text()')
        except Exception as e:
            con_list = ['未知']
        content = ''.join(con_list).strip()
        # log('content', title, date)
        return title, date, content


    def parser_common_item(self, response):
        '''
        解析法律法规  信贷政策
        '''
        try:
            title = response.xpath('//h2[@style="font-size: 16px;color: #333;"]/text()')
            title = ''.join(title).strip()
        except Exception as e:
            title = '未知'

        try:
            date = response.xpath('//span[@id="shijian"]/text()')[0].split()[0]
        except Exception as e:
            date = '未知'
        try:
            con_list = response.xpath('//div[@id="zoom"]/descendant-or-self::*/text()')
        except Exception as e:
            con_list = ['未知']
        content = ''.join(con_list).strip()
        # log('法律法规', content)
        return title, date, content

    def send(self, dest_url, get_news_list, parser_news):
        '''
        获取人行 不同页面的内容 解析 再次请求新闻详情
        :param dest_url:  目标URL
        :param get_news_list: 获取目标URL中的新闻URL
        :param parser_news: 解析新闻中的具体标题 日期等信息
        :return: None
        '''
        content = self.get_html(dest_url)
        urls = get_news_list(content)
        news_list = self.send_request(urls, parser_news)
        for news in news_list:
            self.mgr.insert(news)


    def run(self):
        log_line('PbcSpider 启动！！！')

        # 公告信息
        dest_url = 'http://www.pbc.gov.cn/rmyh/105208/index.html'
        self.send(dest_url, self.parser_gonggao_list, self.parse_gonggao_item)

        # 法律法规
        dest_url = 'http://www.pbc.gov.cn/tiaofasi/144941/index.html'
        self.send(dest_url, self.parser_falvfagui, self.parser_common_item)


        # 货币政策  暂未完成
        # dest_url = 'http://www.pbc.gov.cn/rmyh/105145/index.html'
        # self.send(dest_url, self.parser_xindai, self.parser_common_item)


        # 信贷政策
        dest_url = 'http://www.pbc.gov.cn/jinrongshichangsi/147160/147289/index.html'
        self.send(dest_url, self.parser_xindai, self.parser_common_item)


        self.__class__().re_send()




if __name__ == '__main__':
    PbcSpider().run()
