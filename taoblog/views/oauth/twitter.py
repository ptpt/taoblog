from flask import redirect, url_for

from .oauth import BaseOAuth


class TwitterOAuth(BaseOAuth):
    def __init__(self, app):
        self.remote_app = self.OAUTH.remote_app(
            'twitter',
            base_url = 'https://api.twitter.com/1/',
            request_token_url = 'https://api.twitter.com/oauth/request_token',
            access_token_url = 'https://api.twitter.com/oauth/access_token',
            authorize_url = 'https://api.twitter.com/oauth/authenticate',
            consumer_key = app.config['TWITTER_CONSUMER'][0], # consumer key
            consumer_secret = app.config['TWITTER_CONSUMER'][1]) # consumer secret

        BaseOAuth.__init__(self)

    def find_token(self, resp):
        return resp['oauth_token'], resp['oauth_token_secret']

    def find_identity(self, resp):
        return resp['screen_name']

    def find_form_defaults(self, resp):
        return {'name': resp['screen_name']}
