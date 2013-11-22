# -*- coding: utf-8 -*-

from flask import (Blueprint, request, g, current_app,
                   session, redirect, url_for,
                   abort, flash)

from ..models import Session, ModelError
from ..models.user import User, UserOperator
from .helpers import (save_account_to_session,
                      check_consistency, get_next_url,
                      render_template, login_and_sid_matching_required)
from .oauth import choose_provider, BaseOAuthError


account_bp = Blueprint('account', __name__)
user_op = UserOperator(Session())


account_bp.before_request(check_consistency)


@account_bp.route('/')
def profile():
    next_url = get_next_url()
    if g.is_login:
        session.pop('provider', None)
        session.pop('token', None)
    if g.is_login or ('token' in session and 'provider' in session):
        return render_template('account/profile.html', next=next_url)
    else:
        return redirect(url_for('session.render_login'))


@account_bp.route('/delete', methods=['POST'])
@login_and_sid_matching_required
def delete_user():
    user = user_op.get_user(session['uid'])
    user_op.delete_user(user)
    session.clear()
    flash('You\'ve been logout', category='success')
    flash('Your account has been deleted', category='success')
    session.pop('token', None)
    session.pop('provider', None)
    return redirect(get_next_url())


@account_bp.route('/update', methods=['POST'])
@login_and_sid_matching_required
def update_user():
    kwargs = {}
    name = request.form.get('name')
    if name:
        name = name.strip()
        kwargs['name'] = name
    email = request.form.get('email')
    if email:
        email = email.strip()
        kwargs['email'] = email
    user = user_op.get_user(session['uid'])
    next_url = get_next_url()
    try:
        user_op.update_user(user, **kwargs)
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(url_for('account.profile',
                                next=next_url,
                                name=name,
                                email=email))
    save_account_to_session(user)
    flash('Settings updated', category='success')
    return redirect(next_url)


@account_bp.route('/create', methods=['POST'])
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
        user_op.create_user(account)
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
