import unittest

from taoblog.models import Base, Session, bind_engine
bind_engine('sqlite:///:memory:', echo=False)


class TaoblogTestCase(unittest.TestCase):
    def db_setup(self):
        Base.metadata.create_all()
        self.session = Session()

    def db_teardown(self):
        self.session.close()
        Base.metadata.drop_all()


def get_tests_root():
    import os
    return os.path.dirname(__file__)
