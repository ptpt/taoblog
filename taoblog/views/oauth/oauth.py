from flask import (url_for, flash, redirect, session, Blueprint, request)
from flask_oauth import OAuth

from ...models import Session
from ...models.user import User, UserOperator
from ..helpers import save_account_to_session, unquote_token, quote_token


class BaseOAuth(object):
    OAUTH = OAuth()
    UO = UserOperator(Session())

    remote_app = None

    def __init__(self):
        if self.remote_app is None:
            raise RuntimeError('remote_app is not defined.')

        self.remote_app.tokengetter(self._get_token)
        self.blueprint = Blueprint('oauth_%s' % self.remote_app.name, __name__)
        self.blueprint.add_url_rule('/login/%s' % self.remote_app.name,
                                    endpoint='login',
                                    view_func=self._login)
        self.blueprint.add_url_rule('/login/%s/oauth-authorized' % self.remote_app.name,
                                    endpoint='oauth_authorized',
                                    view_func=self.remote_app.authorized_handler(self._oauth_authorized))

    def _login(self):
        callback = url_for('oauth_%s.oauth_authorized' % self.remote_app.name,
                           next=request.values.get('next'),
                           _external=True)
        return self.remote_app.authorize(callback=callback)

    def _get_token(self):
        if 'token' in session:
            return unquote_token(session['token'])

    def _oauth_authorized(self, resp):
        next_url = request.args.get('next') or request.url_root

        if resp is None:
            flash(u'You denied the request to sign in.', category='error')
            return redirect(next_url)

        session['token'] = quote_token(self.find_token(resp))
        identity = self.find_identity(resp)

        account = self.UO.session.query(User).\
            filter_by(provider=self.remote_app.name).\
            filter_by(identity=identity).first()

        if account:
            # login
            save_account_to_session(account)
            flash('welcome', category='success')
            session.pop('token', None)
            return redirect(next_url)
        else:
            # create account
            session['provider'] = self.remote_app.name
            session['identity'] = identity
            defaults = self.find_form_defaults(resp)
            return redirect(url_for('account.profile', **defaults))

    def find_token(self, resp):
        raise RuntimeError('Required to be implemented.')

    def find_identity(self, resp):
        raise RuntimeError('Required to be implemented.')

    def find_form_defaults(self, resp):
        raise RuntimeError('Required to be implemented.')
