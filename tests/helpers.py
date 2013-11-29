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
app.config['ADMIN_EMAIL'] = ['author@email.com',
                             'admin@email.com']
app.debug = True


class TaoblogTestCase(unittest.TestCase):
    def db_setup(self):
        Base.metadata.create_all()
        self.session = Session()

    def db_teardown(self):
        self.session.close()
        Base.metadata.drop_all()

    @property
    def app(self):
        if not hasattr(self, '_app') or self._app is None:
            self._app = app.test_client()
        return self._app

    def login(self, **data):
        data.setdefault('name', 'user')
        data.setdefault('provider', 'user_provider')
        data.setdefault('identity', 'user_identity')
        data.setdefault('email', 'user@email.com')
        data.setdefault('sid', 'sid')
        rv = self.app.post('/login/testing', data=data)
        assert rv.status_code == 200
        return rv

    def login_as_admin(self):
        return self.login(email=self.app.application.config['ADMIN_EMAIL'][0],
                          identity='admin_identity')

    def logout(self):
        rv = self.app.post('/logout/testing')
        assert rv.status_code == 200
        return rv


def get_tests_root():
    return os.path.dirname(__file__)


from taoblog.models.user import UserOperator
user_op = UserOperator(Session())
from flask import jsonify


@app.route('/login/testing', methods=['POST'])
def login_testing():
    provider = request.form.get('provider')
    identity = request.form.get('identity')
    sid = request.form.get('sid')
    user = user_op.get_user_by_identity(provider=provider,
                                        identity=identity)
    if user is not None:
        save_account_to_session(user, sid=sid)
        return jsonify(request.form)
    user = User(name=request.form.get('name'),
                email=request.form.get('email'),
                provider=request.form.get('provider'),
                identity=request.form.get('identity'))
    user_op.create_user(user)
    save_account_to_session(user, sid=sid)
    return jsonify(request.form)


@app.route('/logout/testing', methods=['GET', 'POST'])
def logout_testing():
    jsonified_session = jsonify(session)
    session.clear()
    return jsonified_session