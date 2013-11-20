__all__ = ['application']

import os
import tempfile
from flask import Flask

from .views import configure_app
from .models import bind_engine

DEBUG = False
DATABASE_ECHO = False
DATABASE_URI = 'sqlite:///%s' % tempfile.mkstemp()[1]
POST_PERPAGE = 8
POST_API_PERPAGE = 20
POST_FEED_PERPAGE = 20
# no one is admin by default
ADMIN_EMAIL = None
BLOG_TITLE = 'Taoblog'
SECRET_KEY = os.urandom(24)
LOCALE = 'en'

application = Flask('taoblog')

application.config.from_object(__name__)

# load config from the file specified by the env var
application.config.from_envvar('TAOBLOG_CONFIG_PATH', silent=True)

# init database
bind_engine(application.config['DATABASE_URI'],
            application.config['DATABASE_ECHO'])

# configure application
configure_app(application)
