# -*- coding=utf-8 -*-
import datetime


def get_time():

    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%m")
    seq_str = '[taotaojin ' + time + '] '
    return seq_str


def log(*args):
    '''打印日志'''
    seq_str = get_time()
    for m in args:
        if isinstance(m, list):
            # 尝试打印列表明细
            for element in m:
                print(seq_str + ' ** ' + str(element))
            continue

        if isinstance(m, dict):
            for k, v in m.items():
                print(seq_str + ' ** ' + str(k) + ' = ' + str(v))
            continue

        seq_str += ' ** ' + str(m)
    if not seq_str.endswith('] '):
        print(seq_str)


def log_line(title=''):
    '''打印分割线'''
    seq_str = get_time()
    print('\n\n')
    print(seq_str + '-' * 20 + str(title) + '-' * 25)


if __name__ == '__main__':
    # 使用案例
    data_dict = {'22': 55, '44': 'dsd'}
    data_list = [12, 'dsad']
    data_int = 1234
    data_str = 'haha'

    log_line()
    log_line('我是分割线中间的标题')

    # 混合数据输出 字典 列表 字符串  int
    log(data_dict, data_list, data_int, data_str)
    log(data_dict, data_list)
    log(data_dict, data_str)
    log(data_dict)
    log(data_list)
    # data_str 主要用于解释data_int的含义
    log(data_int, data_str)
    log(data_str)
