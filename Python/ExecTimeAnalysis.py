# -*- coding:utf-8 -*-
from functools import wraps
import cProfile
import time


def func_time(f):
    """
    简单记录执行时间
    :param f:
    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print f.__name__, 'took', end - start, 'seconds'
        return result

    return wrapper


def func_cprofile(f):
    """
    内建分析器
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = f(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats(sort='time')

    return wrapper

@func_time
@func_cprofile
def test():
    for x in range(100000):
        print x
test()