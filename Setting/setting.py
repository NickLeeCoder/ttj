# -*- coding: utf-8 -*-

class Setting(object):

    # BOT_NAME = 'ttj_pro'
    #
    # SPIDER_MODULES = ['ttj_pro.Spiders']
    # NEWSPIDER_MODULE = 'ttj_pro.Spiders'

    # 保存日志信息的文件名
    LOG_FILE = "ttj_pro.log"
    # 保存日志等级，低于|等于此等级的信息都被保存
    LOG_LEVEL = "DEBUG"

    # 访问超时时间
    DOWNLOAD_TIMEOUT = 50

    # 请求间隔时间
    # DOWNLOAD_DELAY = 1

    # MONGODB 主机名
    MONGODB_HOST = "127.0.0.1"

    # MONGODB 端口号
    MONGODB_PORT = 27017

    # 数据库名称
    MONGODB_DBNAME = "ttj"

    # 存放数据的表名称
    MONGODB_NEWS = "news"


    # 用于存放完成的爬虫名称
    MONGODB_SPIDERS = "Spiders"

    # 启动命令
    # COMMANDS_MODULE = 'ttj_pro.commands'

    # ttj_email-server
    EMAIL_SERVER = 'smtp.163.com'
    SERVER_USER = 'fxxclwk@163.com'
    SERVER_PASSWORD = 'lwk110'


    spiders = {
        'amac': '',
        'bjjrj': '',
        'cbrc': '',
        'cctv': '',
        'circ': '',
        'cnstock': '',
        'cs': '',
        'csrc': '',
        'fangchan': '',
        'gzjrj': '',
        'hexun': '',
        'jingji': '',
        'mohurd': '',
        'pbc': '',
        'shanghai': '',
        'stcn': '',
        'szjrj': '',

    }







    # Override the default request headers:
    DEFAULT_REQUEST_HEADERS = {
      'USER_AGENT' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en',
    }



    USER_AGENTS = [\
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
            "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
           ]



