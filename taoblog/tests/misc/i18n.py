import os
import unittest

from taoblog.i18n import I18n
from taoblog.tests.helpers import get_tests_root

tests_root = get_tests_root()

class TestI18N(unittest.TestCase):
    def test_load(self):
        i18n = I18n()
        self.assertRaises(OSError, I18n.load, i18n, os.path.join(tests_root, 'data/no-such-dir'))
        self.assertFalse(i18n.load(os.path.join(tests_root, 'data/no-such-dir'), silent=True))
        self.assertEqual(len(i18n.locales), 0)
        self.assertTrue(i18n.load(os.path.join(tests_root, 'data/i18n')))
        self.assertTrue('en' in i18n.locales)
        self.assertTrue('cn' in i18n.locales)
        self.assertFalse('tw' in i18n.locales)
        # no LOCALE found in tw.py, then tw is a invalid locale file
        self.assertFalse('tw' in i18n.fallbacks)
        self.assertFalse('tw' in i18n.names)
        self.assertFalse('tw' in i18n.locales)

    def test_localize(self):
        i18n = I18n(os.path.join(tests_root, 'data/i18n'))
        # 'this is cool' not found, raise KeyError
        self.assertRaises(KeyError, I18n.localize, i18n, 'this is cool', 'cn')
        # return value
        self.assertEqual(i18n.localize('hello', 'cn', tao='pt'), 'ni hao pt')
        # no such locale, raise KeyError
        self.assertRaises(KeyError, I18n.localize, i18n, 'KAKAKAKA', 'tw')
        # fallback
        self.assertEqual(i18n.localize('in-default', 'cn'), 'in-default')
        self.assertEqual(i18n.localize('in-default', 'hk'), 'in-default')
        self.assertEqual(i18n.localize('in-cn', 'hk'), 'in-cn')
        self.assertEqual(i18n.localize('in-hk', 'hk'), 'in-hk')
        self.assertTrue(i18n.validate_fallbacks())
