
class News(object):
    '''
    新闻保存的字段
    '''

    def __init__(self, title=None, date=None, content=None, url=None,
                 spider_name=None, is_sended=None, update=None):
        self.title = title                      # 新闻标题
        self.date = date                        # 新闻日期
        self.content = content                  # 新闻内容
        self.url = url                          # 新闻链接
        self.update = update                    # 是否需要更新数据库的新闻
        self.spider_name = spider_name          # 爬虫信息
        self.is_sended = is_sended              # 是否云已发送邮件