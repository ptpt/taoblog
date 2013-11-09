import os
import unittest
from flask import (abort, session,
                   redirect, request, g)

from taoblog import application as app
from taoblog.models import (ModelError, Base,
                            Session, bind_engine)
from taoblog.models.user import User
from taoblog.views.helpers import save_account_to_session, get_next_url


bind_engine('sqlite:///:memory:', echo=False)
app.config['ADMIN_EMAIL'] = ['author@taoblog.com',
                             'admin@taoblog.com']


class TaoblogTestCase(unittest.TestCase):
    def db_setup(self):
        Base.metadata.create_all()
        self.session = Session()

    def db_teardown(self):
        self.session.close()
        Base.metadata.drop_all()


def get_tests_root():
    return os.path.dirname(__file__)


@app.route('/login/testing', methods=['POST'])
def login_testing():
    account = None
    try:
        account = User(name=request.form.get('name'),
                       email=request.form.get('email'),
                       provider=request.form.get('provider'),
                       identity=request.form.get('identity'))
        account.id = 1
    except ModelError:
        abort(400)
    session['sid'] = request.form.get('sid')
    save_account_to_session(account)
    return redirect(get_next_url())


@app.route('/logout/testing', methods=['GET', 'POST'])
def logout_testing():
    if g.is_login and request.values.get('sid') == session.get('sid'):
        session.clear()
    session.pop('token', None)
    session.pop('provider', None)
    return redirect(get_next_url())