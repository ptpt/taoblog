import os
from flask import (request, g, redirect,
                   current_app, jsonify)

from ..models import Base
from ..i18n import I18n
from .helpers import (JumpDirectly, check_login,
                      check_admin, require_admin)

from .post import BP as bp_post
from .api import BP as bp_api
from .account import BP as bp_account
from .admin import BP as bp_admin
from .session import BP as bp_session
from .openid import BP as bp_openid
from .oauth import (TwitterOAuth, FacebookOAuth, GoogleOAuth)


def configure_app(app):
    app.register_blueprint(bp_post)
    app.register_blueprint(bp_api, url_prefix='/api')
    app.register_blueprint(bp_admin, url_prefix='/admin')
    app.register_blueprint(bp_account, url_prefix='/account')
    app.register_blueprint(bp_session)
    app.register_blueprint(bp_openid)

    if 'TWITTER_CONSUMER' in app.config:
        app.register_blueprint(TwitterOAuth(app).blueprint)

    if 'FACEBOOK_CONSUMER' in app.config:
        app.register_blueprint(FacebookOAuth(app).blueprint)

    if 'GOOGLE_CONSUMER' in app.config:
        app.register_blueprint(GoogleOAuth(app).blueprint)

    I18n.create_jinja_environment = app.create_jinja_environment
    i18n = I18n()

    @app.before_first_request
    def setup_template():
        # load default i18n folder
        i18n.load(os.path.join(current_app.root_path, 'i18n'))
        # then load the custom i18n folder
        if 'I18N_FOLDER' in current_app.config:
            # if this folder not found, keep quiet
            i18n.load(current_app.config['I18N_FOLDER'], silent=True)

    @app.context_processor
    def locale_processor():

        def get_locale_name(locale, default=None):
            return i18n.get_locale_name(locale, default)

        def localize(key, locale=None, **kwargs):
            # use your locale
            if locale is None:
                locale = g.locale
            # use default locale
            if locale not in i18n.locales:
                locale = current_app.config.get('LOCALE')
            if locale in i18n.locales:
                try:
                    return i18n.localize(key, locale, **kwargs)
                except KeyError:
                    return key
            else:
                return key

        return {'get_locale_name': get_locale_name,
                'localize': localize}

    @app.before_first_request
    def db_create_all():
        Base.metadata.create_all()

    @app.before_request
    def get_locale():
        g.locale = request.cookies.get('locale')
        g.locales = i18n.names.keys()
        if g.locale not in g.locales:
            # use default locale
            g.locale = current_app.config.get('LOCALE')

    @app.before_request
    def get_session_status():
        g.is_login = check_login()
        g.is_admin = check_admin(current_app)

    @app.route('/set')
    def set_cookie():
        response = redirect(request.values.get('next') or
                            request.referrer or
                            request.url_root)
        locale = request.args.get('locale')
        if locale and locale.lower() in g.locales:
            response.set_cookie('locale', locale.lower())
        return response

    @app.errorhandler(JumpDirectly)
    def handle_view_error(error):
        return error.response

    @app.route('/debug/config')
    def show_config():
        require_admin()
        config = dict(current_app.config)
        config['PERMANENT_SESSION_LIFETIME'] = \
            unicode(config['PERMANENT_SESSION_LIFETIME'])
        del config['SECRET_KEY']
        return jsonify(config)

    @app.route('/debug/globals')
    def show_globals():
        require_admin()
        return jsonify({'locale': g.locale,
                        'locales': g.locales})
