__all__ = ['TestUser', 'TestUserOperator']

import unittest

from taoblog.tests.helpers import TaoblogTestCase
from taoblog.models.user import *
from taoblog.models import ModelError


class TestUser(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_name(self):
        # empty name
        self.assertRaises(ModelError, User,
                          name='\n\t    ',
                          email='pt@taopeng.me',
                          provider='twitter',
                          identity='asas')
        # short name
        self.assertRaises(ModelError, User,
                          name='a',
                          email='pt@taopeng.me',
                          provider='twitter',
                          identity='aaa')
        # long name
        self.assertRaises(ModelError, User,
                          name='a' * 37,
                          email='pt@taopeng.com',
                          provider='twitter',
                          identity='aaa')

    def test_email(self):
        # empty email
        self.assertRaises(ModelError, User,
                          name='pt',
                          email='\t\n     ',
                          provider='twitter',
                          identity='aaa')
        # no @
        self.assertRaises(ModelError, User,
                          name='pt',
                          email='pttaopeng.me',
                          provider='twitter',
                          identity='aaa')
        # no dot
        self.assertRaises(ModelError, User,
                          name='pt',
                          email='pt@taopengme',
                          provider='twitter',
                          identity='hhhh')


class TestUserOperator(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_create_user(self):
        op = UserOperator(self.session)
        user = User(name='pt',
                    email='pt@gmail.com',
                    provider='openid',
                    identity='a secret')
        op.create_user(user)
        self.assertEqual(op.get_user(user.id), user)
        another_user = User(name='pt',
                            email='pt2@gmail.com',
                            provider='openid2',
                            identity='haha')
        self.assertRaises(ModelError, op.create_user, another_user)
