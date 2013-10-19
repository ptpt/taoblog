from rauth import OAuth2Service

from .oauth import BaseOAuth, BaseOAuthError


class FacebookOAuth(BaseOAuth):
    service_name = 'facebook'

    def __init__(self, app):
        self.service = OAuth2Service(
            name=self.service_name,
            base_url='https://graph.facebook.com/',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            client_id=app.config['FACEBOOK_CONSUMER'][0],
            client_secret=app.config['FACEBOOK_CONSUMER'][1])
        super(FacebookOAuth, self).__init__()

    @property
    def authorized_params(self):
        return {'redirect_uri': self.get_redirect_uri()}

    def get_access_token(self, code):
        data = dict(code=code, redirect_uri=self.get_redirect_uri())
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