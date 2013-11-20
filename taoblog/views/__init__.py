from flask import (g, current_app, jsonify)

from ..models import Base
from .helpers import (JumpDirectly, is_login,
                      is_admin, require_admin)

from .post import post_bp
from .api import api_bp
from .account import account_bp
from .admin import admin_bp
from .session import session_bp
from .oauth import (FacebookOAuth, GoogleOAuth)


def configure_app(app):
    app.register_blueprint(post_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(session_bp)

    if 'FACEBOOK_CONSUMER' in app.config:
        app.register_blueprint(FacebookOAuth(app).blueprint)
    if 'GOOGLE_CONSUMER' in app.config:
        app.register_blueprint(GoogleOAuth(app).blueprint)

    @app.before_first_request
    def db_create_all():
        Base.metadata.create_all()

    @app.before_request
    def get_session_status():
        g.is_login = is_login()
        g.is_admin = is_admin(current_app)

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
