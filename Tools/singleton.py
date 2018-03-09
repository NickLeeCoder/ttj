# -*- coding=utf-8 -*-


def singleton(cls, *args, **kw):
    """单例类装饰器"""
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton
