# -*- coding: utf-8 -*-

from flask import (Blueprint, request, g, abort,
                   session, redirect,
                   current_app, render_template, flash)

from ..models import Session, ModelError
from ..models.user import User, UserOperator
from .helpers import check_consistency, save_account_to_session, get_next_url


BP = Blueprint('session', __name__)
UO = UserOperator(Session())


BP.before_request(check_consistency)


@BP.route('/login')
def render_login():
    next_url = get_next_url()
    if g.is_login:
        return redirect(next_url)
    else:
        return render_template('session/login.html', next=next_url)


@BP.route('/logout', methods=['GET', 'POST'])
def logout():
    if g.is_login and request.values.get('sid') == session.get('sid'):
        session.clear()
        flash('You\'ve been logout', category='success')
    # always remove identity from session
    session.pop('identity', None)
    return redirect(get_next_url())


@BP.route('/login/debug', methods=['POST'])
def debug_login():
    if not current_app.config['DEBUG']:
        abort(403)
    try:
        account = User(name=request.form.get('name'),
                       email=request.form.get('email'),
                       provider=request.form.get('provider'),
                       identity=request.form.get('identity'))
        account.id = 1
    except ModelError:
        abort(400)
    session['sid'] = request.form.get('sid')
    save_account_to_session(account)
    return redirect(get_next_url())


@BP.route('/logout/debug', methods=['GET', 'POST'])
def debug_logout():
    if not current_app.config['DEBUG']:
        abort(403)
    if g.is_login and request.values.get('sid') == session.get('sid'):
        session.clear()
    # always remove identity from session
    session.pop('identity', None)
    return redirect(get_next_url())
