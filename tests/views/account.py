import unittest
import json

import taoblog
from ..helpers import TaoblogTestCase

class AccountTestCase(TaoblogTestCase):
    def setUp(self):
        self.db_setup()
        taoblog.application.config['DEBUG'] = True
        taoblog.application.config['ADMIN_EMAIL'] = ['admin@gmail.com', 'admin2@gmail.com']
        self.app = taoblog.application.test_client()

    def tearDown(self):
        self.db_teardown()

    def test_login(self):
        pass

    def test_logout(self):
        pass
