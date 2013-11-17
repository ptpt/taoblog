# -*- coding: utf-8 -*-

from flask import (Blueprint, current_app as app,
                   g, request, flash,
                   url_for, abort, redirect)

from ..models import Session, ModelError
from ..models.post import Post, PostOperator
from ..helpers import get_date_range
from .helpers import require_admin, render_template

admin_bp = Blueprint('admin', __name__)
post_op = PostOperator(Session())


admin_bp.before_request(require_admin)


@admin_bp.route('/')
def render_dashboard():
    return render_template('admin/compose.html')


def get_status_code(status_string):
    """ Parse status string like public+private into a list of status code. """
    statuses = status_string.lower().split('+')
    status_code = []
    for status in set(statuses):
        if status == 'public':
            status_code.append(Post.STATUS_PUBLIC)
        elif status == 'private':
            status_code.append(Post.STATUS_PRIVATE)
            if not g.is_admin:
                abort(403)
        elif status == 'trash':
            status_code.append(Post.STATUS_TRASH)
            if not g.is_admin:
                abort(403)
        else:
            abort(400)
    if len(status_code) == 0:
        abort(400)
    return status_code[0] if len(status_code) == 1 else status_code


@admin_bp.route('/posts/<string:status>/tagged/<string:tags>')
@admin_bp.route('/posts/<string:status>/tagged/<string:tags>/<int:year>/<int:month>')
@admin_bp.route('/posts/<string:status>/tagged/<string:tags>/<int:year>')
@admin_bp.route('/posts/<string:status>/<int:year>')
@admin_bp.route('/posts/<string:status>/<int:year>/<int:month>')
@admin_bp.route('/posts/<string:status>/')
@admin_bp.route('/posts/')
def render_posts(status='public+private', year=None, month=None, tags=None):
    sort = request.args.get('sort', 'created_at')
    asc = 'asc' in request.args
    status_code = get_status_code(status)
    try:
        date_range = year and get_date_range(year, month)
    except (ValueError, TypeError):
        abort(400)
    try:
        posts, more = post_op.query_posts(status=status_code,
                                     limit=app.config['POST_PERPAGE'],
                                     tags=tags and tags.split('+'),
                                     date=date_range,
                                     sort=sort,
                                     asc=asc)
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(url_for('admin.render_posts',
                                year=year, month=month, tags=tags))
    return render_template('admin/posts.html',
                           more=more,
                           status=status,
                           posts=posts)


@admin_bp.route('/drafts/')
def render_drafts():
    drafts = post_op.get_drafts(limit=None)
    return render_template('admin/drafts.html', drafts=drafts)


@admin_bp.route('/compose')
def render_compose():
    return render_template('admin/compose.html')
