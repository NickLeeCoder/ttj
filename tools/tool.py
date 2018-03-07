

import random
import base64

from setting.setting import Setting


# 随机的User-Agent
def randomUserAgent():
    return random.choice(Setting.USER_AGENTS)
