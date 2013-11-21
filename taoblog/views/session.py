# -*- coding: utf-8 -*-

from flask import (Blueprint, g,
                   session, redirect, flash)

from ..models import Session
from ..models.user import UserOperator
from .helpers import (check_consistency,
                      login_and_sid_required,
                      render_template, get_next_url)


session_bp = Blueprint('session', __name__)
user_op = UserOperator(Session())


session_bp.before_request(check_consistency)


@session_bp.route('/login')
def render_login():
    next_url = get_next_url()
    if g.is_login:
        return redirect(next_url)
    else:
        return render_template('session/login.html', next=next_url)


@session_bp.route('/logout', methods=['GET', 'POST'])
@login_and_sid_required
def logout():
    session.clear()
    flash('You\'ve been logout', category='success')
    session.pop('token', None)
    session.pop('provider', None)
    return redirect(get_next_url())