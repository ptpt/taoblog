import random
from flask import (session, flash, g, redirect,
                   abort, url_for, request)

from ..models import Session
from ..models.user import UserOperator


UO = UserOperator(Session())


def check_consistency():
    """
    check if account info stored in the session is consistent
    with the info in the database. if not then clear session.
    """
    if 'uid' not in session:
        return
    account = UO.get_user(session['uid'])
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


def check_login():
    return set(session).issuperset(('uid', 'name', 'email', 'sid'))


def require_login():
    if not g.is_login:
        raise JumpDirectly(
            redirect(url_for('session.render_login', next=request.url)))


def check_admin(app):
    if check_login():
        admin_email = app.config.get('ADMIN_EMAIL')
        if isinstance(admin_email, basestring):
            if admin_email == '*':
                is_admin = True
            else:
                is_admin = session['email'].lower() == \
                    admin_email.lower()
        elif admin_email:
            is_admin = session['email'].lower() in \
                set(email.lower() for email in admin_email)
        else:
            is_admin = False
    else:
        is_admin = False

    return is_admin


def require_admin():
    if not g.is_admin:
        if g.is_login:
            abort(403)
        raise JumpDirectly(
            redirect(url_for('session.render_login', next=request.url)))


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
