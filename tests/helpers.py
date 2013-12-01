import os
import json
import unittest
from flask import (session, request)

from taoblog import application as app
from taoblog.models import (Base, Session, bind_engine)
from taoblog.models.user import User
from taoblog.views.helpers import save_account_to_session


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

    def add_post(self, **data):
        rv = self.client.post('/api/posts/', data=data)
        assert rv.status_code == 200
        return rv

    @property
    def client(self):
        if not hasattr(self, '_client') or self._client is None:
            self._client = app.test_client()
        return self._client

    def login(self, **data):
        data.setdefault('name', 'user')
        data.setdefault('provider', 'user_provider')
        data.setdefault('identity', 'user_identity')
        data.setdefault('email', 'user@email.com')
        data.setdefault('sid', 'sid')
        rv = self.client.post('/login/testing', data=data)
        assert rv.status_code == 200
        return json.loads(rv.data)

    def login_as_admin(self):
        return self.login(email=self.client.application.config['ADMIN_EMAIL'][0],
                          identity='admin_identity')

    def logout(self):
        rv = self.client.post('/logout/testing')
        assert rv.status_code == 200
        return json.loads(rv.data)


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
        return jsonify(user.as_dict())
    user = User(name=request.form.get('name'),
                email=request.form.get('email'),
                provider=request.form.get('provider'),
                identity=request.form.get('identity'))
    user_op.create_user(user)
    save_account_to_session(user, sid=sid)
    return jsonify(user.as_dict())


@app.route('/logout/testing', methods=['GET', 'POST'])
def logout_testing():
    user_id = session['uid']
    session.clear()
    user = user_op.get_user(user_id)
    return jsonify(user.as_dict())