#!/usr/bin/env python3
# -*- coding:UTF-8 -*-
# 正则表达式库

import re


def str_del_non_num(mstr):
        '''
        清洗字符串中非数字字符
        '''
        result = re.sub("\D", "", mstr)
        return result

if __name__ == "__main__":

        from datetime import datetime
        test = str(datetime.now())
        print (str_del_non_num(test))
