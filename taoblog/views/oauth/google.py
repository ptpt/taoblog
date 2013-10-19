import json
from rauth import OAuth2Service

from .oauth import BaseOAuth, BaseOAuthError


class GoogleOAuth(BaseOAuth):
    service_name = 'google'

    def __init__(self, app):
        self.service = OAuth2Service(
            name=self.service_name,
            base_url='https://www.googleapis.com',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            client_id=app.config['GOOGLE_CONSUMER'][0],
            client_secret=app.config['GOOGLE_CONSUMER'][1])
        super(GoogleOAuth, self).__init__()

    @property
    def authorized_params(self):
        return {'redirect_uri': self.get_redirect_uri(),
                'response_type': 'code',
                'scope': 'email profile'}

    def get_access_token(self, code):
        data = dict(code=code,
                    redirect_uri=self.get_redirect_uri(),
                    grant_type='authorization_code')
        return self.service.get_access_token(data=data, decoder=json.loads)

    def get_identity(self, token):
        _, _, identity = self.get_user_info(token)
        return identity

    def get_user_info(self, token):
        auth_session = self.service.get_session(token)
        json = auth_session.get('/oauth2/v2/userinfo').json()
        if 'error' in json:
            raise BaseOAuthError(json['error']['message'])
        return json['name'], json['email'], json['id']