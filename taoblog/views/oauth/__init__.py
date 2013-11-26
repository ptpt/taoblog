from .oauth import BaseOAuthError, BaseOAuth
from .facebook import FacebookOAuth
from .google import GoogleOAuth


providers = dict((p.service_name, p)
                 for p in (FacebookOAuth, GoogleOAuth))