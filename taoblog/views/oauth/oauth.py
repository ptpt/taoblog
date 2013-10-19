from flask import (url_for, flash, redirect, session, Blueprint, request)

from ...models import Session
from ...models.user import User, UserOperator
from ..helpers import save_account_to_session


class BaseOAuthError(Exception):
    pass


class BaseOAuth(object):
    user_op = UserOperator(Session())
    service = None
    service_name = None
    authorized_params = {}

    def __init__(self):
        if self.service is None or self.service_name is None:
            raise RuntimeError('service is not defined.')

        self.blueprint = Blueprint('oauth_%s' % self.service_name, __name__)
        self.blueprint.add_url_rule('/login/%s' % self.service_name,
                                    endpoint='login',
                                    view_func=self._login)
        self.blueprint.add_url_rule('/login/%s/authorized' % self.service_name,
                                    endpoint='authorized',
                                    view_func=self._authorized)

    def _login(self):
        return redirect(self.service.get_authorize_url(**self.authorized_params))

    def _authorized(self):
        next_url = request.args.get('next') or request.url_root

        if 'code' not in request.args:
            flash('You did not authorize the request')
            return redirect(next_url)

        code = request.args['code']
        token = self.get_access_token(code)
        name, email, identity = self.get_user_info(token)

        account = self.user_op.session.query(User).\
            filter_by(provider=self.service_name).\
            filter_by(identity=identity).first()

        if account:
            ## login
            save_account_to_session(account)
            flash('welcome', category='success')
            return redirect(next_url)
        else:
            ## create account
            session['token'] = token
            session['provider'] = self.service_name
            params = {'next': next_url,
                      'name': name,
                      'email': email}
            return redirect(url_for('account.profile', **params))

    def get_redirect_uri(self):
        return url_for('oauth_%s.authorized' % self.service_name,
                       _external=True,
                       next=request.values.get('next'))

    def get_identity(self, token):
        """
        Get user identity from the provider.

        The identity and provider are used to
        identify that you are real user on the provider,
        and they must be unique.
        """
        raise RuntimeError('Required to be implemented')

    def get_access_token(self, code):
        """ Exchange code for an access token """
        raise RuntimeError('Required to be implemented')

    def get_user_info(self, token):
        """ Get a list of name, email, identity from the provider """
        raise RuntimeError('Required to be implemented')