

import random
import base64
from datetime import datetime
from Setting.setting import Setting

cc = 0

# 随机的User-Agent
def randomUserAgent():
    return random.choice(Setting.USER_AGENTS)


def get_today():
    now = datetime.now()
    return now.year, now.month, now.day


def get_keyword():
    '''
    需要过滤的关键字
    :return:
    '''
    return [
        '资产管理',
        '资产证券化',
        '委托贷款',
        '同业',
        '信托',
        '基金',
        '资产管理计划',
        '信托计划',
        '货币政策',
        '信贷政策',
        '非标',
        '小额贷款',
        '房产抵押',
        '私募股权',
        '并购重组',
        '理财',

    ]


def has_keywords(item):
    '''
    检查一个item 是否有敏感关键字
    :param item:
    :return:
    '''
    keywords = get_keyword()

    for val in keywords:
        if val in item['content'] or val in item['title']:
            print('该新闻有敏感关键字 需要发送邮件', val, item['url'])
            global cc
            cc += 1
            print('发邮件的新闻' + str(cc))
            return True
    return False


if __name__ == '__main__':
    y, m, d =  get_today()

    if m < 10:
        print('小鱼10')

    print(type(m))