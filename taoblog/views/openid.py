from flask import (Blueprint, request,
                   session, redirect, url_for,
                   render_template, flash)
from flask_openid import OpenID

from ..models import Session
from ..models.user import User, UserOperator
from .helpers import (check_consistency,
                      save_account_to_session,
                      get_next_url)


BP = Blueprint('openid', __name__)
UO = UserOperator(Session())
OID = OpenID()


BP.before_request(check_consistency)


@BP.route('/login/openid', methods=['POST', 'GET'])
@OID.loginhandler
def openid_login():
    if request.method == 'GET':
        return redirect(url_for('session.render_login', next=get_next_url()))
    url = request.values.get('openid')
    if url:
        return OID.try_login(url, ask_for=['email', 'fullname'])
    else:
        flash('No openid provided', category='error')
        return render_template('session/login.html', next=get_next_url())


@OID.after_login
def after_openid_login(response):
    next_url = get_next_url()
    account = UO.session.query(User).\
        filter_by(provider='openid').\
        filter_by(identity=response.identity_url).first()
    if account:
        # login successfully
        save_account_to_session(account)
        flash('welcome', category='success')
        return redirect(next_url)
    else:
        # create account
        session['provider'] = 'openid'
        session['identity'] = response.identity_url
        return redirect(url_for('account.profile',
                                next=next_url,
                                name=response.fullname,
                                email=response.email))
