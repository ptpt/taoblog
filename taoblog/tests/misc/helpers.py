#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
from datetime import datetime
from flask import Flask

from taoblog.helpers import (Pagination, chinese_numeralize)
from taoblog.tests.helpers import get_tests_root


tests_root = get_tests_root()


class TestDigitize(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_cn_digitize(self):
        # print cn_digitize(1)
        self.assertEqual(chinese_numeralize(1), u'一')
        self.assertEqual(chinese_numeralize(10), u'十')
        self.assertEqual(chinese_numeralize(100), u'一百')
        self.assertEqual(chinese_numeralize(1000), u'一千')

        self.assertEqual(chinese_numeralize(10000), u'一万')
        self.assertEqual(chinese_numeralize(100000), u'十万')
        self.assertEqual(chinese_numeralize(1000000), u'一百万')
        self.assertEqual(chinese_numeralize(10000000), u'一千万')
        self.assertEqual(chinese_numeralize(100000000), u'一亿')
        self.assertEqual(chinese_numeralize(1000000000), u'十亿')
        self.assertEqual(chinese_numeralize(10000000000), u'一百亿')
        self.assertEqual(chinese_numeralize(2000000000000000), u'两千万亿')
        self.assertEqual(chinese_numeralize(10000000000000001), u'一亿亿零一')

        # print cn_digitize(1000200012345)
        self.assertEqual(chinese_numeralize(12345),u'一万两千三百四十五')
        self.assertEqual(chinese_numeralize(1000200012325),u'一万零两亿零一万两千三百二十五')
        self.assertEqual(chinese_numeralize(0),u'零')
        self.assertEqual(chinese_numeralize(000),u'零')
        self.assertEqual(chinese_numeralize(2),u'两')
        self.assertEqual(chinese_numeralize(12),u'十二')
        self.assertEqual(chinese_numeralize(22),u'二十二')
        # print cn_digitize(222)
        self.assertEqual(chinese_numeralize(222),u'两百二十二')


# class TestPagination(unittest.TestCase):
#     def test_all(self):
#         a = Pagination(['a1', 'b1', 'c1',
#                         'a2', 'b2', 'c2',
#                         'a3', 'b3', 'c3',
#                         'a4', 'b4'], 3)
#         self.assertEqual(a.get(1), ['a1', 'b1', 'c1'])
#         self.assertEqual(a.get(2), ['a2', 'b2', 'c2'])
#         self.assertEqual(a.get(4), ['a4', 'b4'])
#         self.assertEqual(a.total_pages, 4)
#         a = Pagination(['a1', 'b1'], 3)
#         self.assertEqual(a.get(1), ['a1', 'b1'])
#         self.assertEqual(a.total_pages, 1)


if __name__ == '__main__':
    pass
