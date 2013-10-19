from .oauth import BaseOAuthError
from .facebook import FacebookOAuth


def choose_provider(name):
    if name == 'facebook':
        return FacebookOAuth
    else:
        raise RuntimeError('invalid provider')