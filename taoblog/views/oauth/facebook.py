from flask import url_for, request
from rauth import OAuth2Service

from .oauth import BaseOAuth, BaseOAuthError


class FacebookOAuth(BaseOAuth):
    def __init__(self, app):
        self.service = OAuth2Service(
            name='facebook',
            base_url='https://graph.facebook.com/',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            client_id=app.config['FACEBOOK_CONSUMER'][0],
            client_secret=app.config['FACEBOOK_CONSUMER'][1])
        super(FacebookOAuth, self).__init__()

    def get_access_token(self, code):
        redirect_uri = url_for('oauth_%s.authorized' % self.service.name,
                               _external=True,
                               next=request.values.get('next'))
        data = dict(code=code, redirect_uri=redirect_uri)
        return self.service.get_access_token(data=data)

    def get_identity(self, token):
        _, _, identity = self.get_user_info(token)
        return identity

    def get_user_info(self, token):
        auth_session = self.service.get_session(token)
        json = auth_session.get('me').json()
        if 'error' in json:
            raise BaseOAuthError(json['error']['message'])
        return json['name'], json['email'], json['id']