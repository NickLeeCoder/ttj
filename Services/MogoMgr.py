

import pymongo
from Setting.setting import Setting
from pymongo.errors import DuplicateKeyError
from Tools.singleton import singleton
from Tools.log import log_line, log
from Tools.tool import has_keywords


@singleton
class MogoMgr(object):
    def __init__(self, sheetname=Setting.MONGODB_NEWS):
        self.host = Setting.MONGODB_HOST
        self.port = Setting.MONGODB_PORT
        self.dbname = Setting.MONGODB_DBNAME

        # 创建MONGODB数据库链接
        client = pymongo.MongoClient(host = self.host, port = self.port)
        # 指定数据库
        mydb = client[self.dbname]
        # 存放数据的数据库表名
        self.sheet = mydb[sheetname]
        # 建索引
        self.sheet.ensure_index('url', unique=True)

    def insert(self, item):
        item = item.__dict__
        if has_keywords(item):
            item['show_sended'] = '1'
            log('含有敏感关键字')

        log('插入数据')
        try:
            self.sheet.insert(item)
        except DuplicateKeyError as e:
            log('数据重复 无需插入', item['url'])

    def update(self, item):
        self.sheet.update({'url':item['url']}, {'$set': item})

    def find_one(self, key, value):
        return self.sheet.find_one({key:value})

    def remove_all(self):
        self.sheet.remove()

    def get_news(self):
        # 获取需要发送的新闻
        return self.sheet.find({'show_sended': '1', 'is_sended': '0'})

    def count(self):
        return self.sheet.find().count()

    def is_inside(self, key, value):
        pass



if __name__ == '__main__':
    a = MogoMgr()
    b = MogoMgr()
    c = MogoMgr()
    d = MogoMgr()

    print(a)
    print(b)
    print(c)
    print(d)

