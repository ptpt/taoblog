# -*- coding: utf-8 -*-

from flask import (Blueprint, request, g, current_app,
                   session, redirect, url_for,
                   abort, flash)

from ..models import Session, ModelError
from ..models.user import User, UserOperator
from .helpers import (save_account_to_session,
                      check_consistency, get_next_url,
                      render_template)
from .oauth import choose_provider, BaseOAuthError


BP = Blueprint('account', __name__)
UO = UserOperator(Session())


BP.before_request(check_consistency)


@BP.route('/')
def profile():
    next_url = get_next_url()
    if g.is_login:
        session.pop('provider', None)
        session.pop('token', None)
    if g.is_login or ('token' in session and 'provider' in session):
        return render_template('account/profile.html', next=next_url)
    else:
        return redirect(url_for('session.render_login'))


@BP.route('/delete', methods=['POST'])
def delete_user():
    if not g.is_login:
        # todo: clear session fields
        abort(403)
    if request.values.get('sid') == session.get('sid'):
        user = UO.get_user(session['uid'])
        UO.delete_user(user)
        session.clear()
        flash('You\'ve been logout', category='success')
        flash('Your account has been deleted', category='success')
    session.pop('token', None)
    session.pop('provider', None)
    return redirect(get_next_url())


@BP.route('/update', methods=['POST'])
def update_user():
    if not g.is_login:
        # todo: clear session fields
        abort(403)
    kwargs = {}
    name = request.form.get('name')
    if name:
        name = name.strip()
        kwargs['name'] = name
    email = request.form.get('email')
    if email:
        email = email.strip()
        kwargs['email'] = email
    user = UO.get_user(session['uid'])
    next_url = get_next_url()
    try:
        UO.update_user(user, **kwargs)
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(url_for('account.profile',
                                next=next_url,
                                name=name,
                                email=email))
    save_account_to_session(user)
    flash('Settings updated', category='success')
    return redirect(next_url)


@BP.route('/create', methods=['POST'])
def create_user():
    if not ('provider' in session and 'token' in session):
        abort(403)
    next_url = get_next_url()
    name = request.form.get('name')
    email = request.form.get('email')
    provider = session['provider']
    token = session['token']
    ProviderOAuth = choose_provider(provider)
    try:
        identity = ProviderOAuth(current_app).get_identity(token)
    except BaseOAuthError as err:
        session.pop('provider')
        session.pop('token')
        flash(err.message, category='error')
        return redirect(url_for('session.render_login'))

    try:
        account = User(name=name,
                       email=email,
                       provider=provider,
                       identity=identity)
        UO.create_user(account)
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(url_for('account.profile',
                                next=next_url,
                                name=name,
                                email=email))
    else:
        session.pop('provider', None)
        session.pop('token', None)
        save_account_to_session(account)
        flash('New account created', category='success')
        return redirect(next_url)
