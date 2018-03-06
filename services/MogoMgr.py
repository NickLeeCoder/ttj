

import pymongo
import json
from setting.setting import Setting
from pymongo.errors import DuplicateKeyError
from tools.singleton import singleton
from tools.log import log_line, log


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
        log('插入数据')
        try:
            self.sheet.insert(item)
        except DuplicateKeyError as e:
            log_line('插入出错')

    def update(self, item):
        self.sheet.update({'url':item['url']}, {'$set': item})

    def find_one(self, key, value):
        return self.sheet.find_one({key:value})

    def remove_all(self):
        self.sheet.remove()

    def get_news(self):
        # 获取需要发送的新闻
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

