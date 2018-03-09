
class News(object):
    '''
    新闻保存的字段
    '''

    def __init__(self, title=None, date=None, content=None, url=None,
                 spider_name=None, is_sended=None, show_sended=None):
        self.title = title                      # 新闻标题
        self.date = date                        # 新闻日期
        self.content = content                  # 新闻内容
        self.url = url                          # 新闻链接
        self.spider_name = spider_name          # 爬虫信息
        self.is_sended = is_sended              # 是否已发送邮件
        self.show_sended = show_sended          # 是否需要发送邮件（是否包含关键字）
