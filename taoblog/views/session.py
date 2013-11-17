# -*- coding: utf-8 -*-

from flask import (Blueprint, request, g, abort,
                   session, redirect,
                   current_app, render_template, flash)

from ..models import Session, ModelError
from ..models.user import User, UserOperator
from .helpers import (check_consistency, save_account_to_session,
                      render_template, get_next_url)


session_bp = Blueprint('session', __name__)
UO = UserOperator(Session())


session_bp.before_request(check_consistency)


@session_bp.route('/login')
def render_login():
    next_url = get_next_url()
    if g.is_login:
        return redirect(next_url)
    else:
        return render_template('session/login.html', next=next_url)


@session_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if g.is_login and request.values.get('sid') == session.get('sid'):
        session.clear()
        flash('You\'ve been logout', category='success')
    session.pop('token', None)
    session.pop('provider', None)
    return redirect(get_next_url())