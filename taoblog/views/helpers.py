import random
from functools import wraps
from flask import (session, flash, g, redirect,
                   abort, url_for, request,
                   render_template as flask_render_template)

from ..models import Session
from ..models.user import UserOperator


user_op = UserOperator(Session())


def render_template(template_name, **context):
    assert isinstance(template_name, basestring)
    base_template_name = '{0}/{1}'.format('base', template_name)
    return flask_render_template(base_template_name, **context)


def check_consistency():
    """
    check if account info stored in the session is consistent
    with the info in the database. if not then clear session.
    """
    if 'uid' not in session:
        return
    account = user_op.get_user(session['uid'])
    if not (account and
            account.id == session['uid']
            and 'email' in session
            and account.email == session['email']
            and 'name' in session
            and account.name == session['name']
            and 'sid' in session):
        session.clear()
        flash('Inconsistent session', category='error')
        raise JumpDirectly(redirect(get_next_url()))


def generate_sid():
    choices = '0123456789qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM'
    return ''.join([random.choice(choices) for _ in xrange(24)])


def save_account_to_session(account):
    """ save the account information to the session. """
    session['uid'] = account.id
    session['name'] = account.name
    session['email'] = account.email
    session['sid'] = generate_sid()
    session.permanent = True


# todo: give it a better name
class JumpDirectly(Exception):
    def __init__(self, response):
        Exception.__init__(self)
        self.response = response


def require_int(value, code_or_exception):
    try:
        value = int(value)
    except (ValueError, TypeError):
        if isinstance(code_or_exception, Exception):
            raise code_or_exception
        else:
            abort(int(code_or_exception))
    return value


def is_login():
    return set(session).issuperset(('uid', 'name', 'email', 'sid'))


def require_login():
    if not g.is_login:
        raise JumpDirectly(
            redirect(url_for('session.render_login', next=request.url)))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        require_login()
        return f(*args, **kwargs)
    return decorated_function


def is_admin(app):
    if is_login():
        admin_email = app.config.get('ADMIN_EMAIL')
        if isinstance(admin_email, basestring):
            if admin_email == '*':
                admin_or_not = True
            else:
                admin_or_not = session['email'].lower() == \
                    admin_email.lower()
        elif admin_email:
            admin_or_not = session['email'].lower() in \
                set(email.lower() for email in admin_email)
        else:
            admin_or_not = False
    else:
        admin_or_not = False
    return admin_or_not


def require_admin():
    if not g.is_admin:
        if g.is_login:
            abort(403)
        raise JumpDirectly(
            redirect(url_for('session.render_login', next=request.url)))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        require_admin()
        return f(*args, **kwargs)
    return decorated_function


def require_sid():
    if 'sid' not in request.values:
        abort(403)
    if 'sid' not in session:
        abort(403)
    if session['sid'] != request.values['sid']:
        abort(403)


def login_and_sid_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        require_login()
        require_sid()
        return f(*args, **kwargs)
    return decorated_function


def admin_and_sid_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        require_admin()
        require_sid()
        return f(*args, **kwargs)
    return decorated_function


def get_next_url():
    next_url = request.values.get('next') or \
        request.referrer or \
        request.url_root
    if isinstance(next_url, unicode):
        # flash seems to urlencode an unicode url before redirect it.
        # That will cause a already urlencoded unicode url urlencode again
        # so here I encode unicode url to byte string to
        # avoid the double urlencode happening.
        next_url = next_url.encode('utf-8')
    return str(next_url)