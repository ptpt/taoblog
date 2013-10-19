from .oauth import BaseOAuthError
from .facebook import FacebookOAuth
from .google import GoogleOAuth


def choose_provider(name):
    for provider in (FacebookOAuth, GoogleOAuth):
        if name == provider.service_name:
            return provider
    raise RuntimeError('invalid provider')