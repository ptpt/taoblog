from flask import Blueprint, request, url_for, redirect
import rauth

class GoogleOAuth(object):
    def __init__(self, app):
        self.app = app
        self.me = None
        self.blueprint = Blueprint('oauth_google', __name__)
        self.remote_app = rauth.OAuth2Service(
            name='google',
            client_id=app.config['GOOGLE_CONSUMER'][0],
            client_secret=app.config['GOOGLE_CONSUMER'][1],
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://www.google.com/accounts')

        self.blueprint = Blueprint('oauth_google', __name__)
        self.blueprint.add_url_rule('/login/google',
                                    endpoint='login',
                                    view_func=self._login)
        self.blueprint.add_url_rule('/login/google/oauth-authorized',
                                    endpoint='oauth_authorized',
                                    view_func=self._oauth_authorized)


    def _login(self):
        params = {'scope': 'https://www.googleapis.com/auth/userinfo.email',
                  'response_type': 'code',
                  'redirect_uri': url_for('oauth_google.oauth_authorized', _external=True)}
        authorize_url = self.remote_app.get_authorize_url(**params)
        return redirect(authorize_url)

    def _oauth_authorized(self):
        data = {'code': request.args['code'],
                'grant_type': 'authorization_code',
                'redirect_uri': url_for('oauth_google.oauth_authorized', _external=True)}
        import json
        sess = self.remote_app.get_auth_session(data=data, decoder=json.loads)
        resp = sess.request('GET', 'http://httpbin.org/headers', bearer_auth=True)
        return 'google'
