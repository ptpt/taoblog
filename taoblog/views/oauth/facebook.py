from flask import redirect, url_for

from ..helpers import get_next_url
from .oauth import BaseOAuth


class FacebookOAuth(BaseOAuth):
    def __init__(self, app):
        self.me = None
        self.remote_app = BaseOAuth.OAUTH.remote_app(
            'facebook',
            base_url='https://graph.facebook.com/',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            consumer_key=app.config['FACEBOOK_CONSUMER'][0],
            consumer_secret=app.config['FACEBOOK_CONSUMER'][1],
            request_token_params={'scope': 'email'})
        BaseOAuth.__init__(self)

    def find_token(self, response):
        return response['access_token'], ''

    def find_identity(self, response):
        if not self.me:
            self.me = self.remote_app.get('/me')
        return self.me.data.get('id') # The user's Facebook ID

    def find_form_defaults(self, response):
        if not self.me:
            self.me = self.remote_app.get('/me')
        return {'next': get_next_url(),
                'name': self.me.data.get('name'), # The user's full name
                'email': self.me.data.get('email')}
