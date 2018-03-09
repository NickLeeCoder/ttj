

import random
import base64
from datetime import datetime
from Setting.setting import Setting


# 随机的User-Agent
def randomUserAgent():
    return random.choice(Setting.USER_AGENTS)


def get_today():
    now = datetime.now()
    return now.year, now.month, now.day


if __name__ == '__main__':
    y, m, d =  get_today()

    if m < 10:
        print('小鱼10')

    print(type(m))