from flask import (Blueprint, current_app as app,
                   request, flash,
                   url_for, abort, redirect, session)
from werkzeug.contrib.atom import AtomFeed
from datetime import datetime

from ..helpers import slugify, get_date_range, Pagination
from ..models import Session, ModelError
from ..models.post import Post, Draft, PostOperator
from ..models.user import UserOperator
from .helpers import require_int, JumpDirectly, admin_required, render_template


post_bp = Blueprint('post', __name__)
PO = PostOperator(Session())
UO = UserOperator(Session())


@post_bp.route('/feed/')
def atom_feed():
    posts, _ = PO.get_public_posts(limit=app.config['POST_FEED_PERPAGE'])
    feed = AtomFeed(app.config.get('BLOG_TITLE'),  # todo: use settings
                    feed_url=url_for('post.atom_feed', _external=True),
                    url=request.url_root,
                    subtitle=app.config.get('BLOG_SUBTITLE'))  # todo: use settings
    for post in posts:
        author = UO.get_user(user_id=post.author_id)
        feed.add(post.title,
                 post.content,
                 content_type='html',
                 author=author.name,
                 url=url_for('post.render_post_by_permalink',
                             slug=post.slug,
                             year=post.created_year,
                             month=post.created_month),
                 id=post.id,
                 updated=post.updated_at or post.created_at,
                 published=post.created_at)
    return feed.get_response()


@post_bp.route('/<int:year>/<int:month>/')
@post_bp.route('/<int:year>/')
@post_bp.route('/tagged/<string:tags>/<int:year>/<int:month>')
@post_bp.route('/tagged/<string:tags>/<int:year>/')
@post_bp.route('/tagged/<string:tags>/')
@post_bp.route('/')
def render_posts(year=None, month=None, tags=None):
    page = require_int(
        request.args.get('page', 1),
        JumpDirectly(redirect(url_for('post.render_posts',
                                      year=year,
                                      month=month,
                                      tags=tags))))
    try:
        date_range = year and get_date_range(year, month)
    except (ValueError, TypeError):
        abort(400)
    posts, more = PO.get_public_posts(
        offset=(page - 1) * app.config['POST_PERPAGE'],
        limit=app.config['POST_PERPAGE'],
        tags=tags and tags.split('+'),
        date=date_range)

    def _page_generator(page):
        return url_for('post.render_posts',
                       page=page, year=year,
                       month=month, tags=tags)

    pagination = Pagination(page, more, _page_generator)
    return render_template('post/posts.html', posts=posts,
                           tags=tags and tags.split('+'),
                           pagination=pagination)


@post_bp.route('/archive/<int:year>/<int:month>/')
@post_bp.route('/archive/<int:year>/')
@post_bp.route('/archive/tagged/<string:tags>/<int:year>/<int:month>/')
@post_bp.route('/archive/tagged/<string:tags>/<int:year>/')
@post_bp.route('/archive/tagged/<string:tags>/')
@post_bp.route('/archive/')
def archive(year=None, month=None, tags=None):
    page = require_int(
        request.args.get('page', 1),
        JumpDirectly(redirect(url_for('.render_posts',
                                      year=year,
                                      month=month,
                                      tags=tags))))
    date_range = None
    try:
        date_range = year and get_date_range(year, month)
    except (ValueError, TypeError):
        abort(400)
    posts, more = PO.get_public_posts(
        offset=(page - 1) * app.config['POST_PERPAGE'],
        limit=app.config['POST_PERPAGE'],
        tags=tags and tags.split('+'), date=date_range)

    def _page_generator(page):
        return url_for('post.archive',
                       page=page, year=year,
                       month=month, tags=tags)

    pagination = Pagination(page, more, _page_generator)
    return render_template('post/archive.html', posts=posts,
                           tags=tags and tags.split('+'),
                           tagcloud=PO.get_public_tags(),
                           pagination=pagination)


@post_bp.route('/<int:year>/<int:month>/<string:slug>')
def render_post_by_permalink(slug, year, month):
    post = None
    try:
        post = PO.get_post_by_permalink(slug, year=year, month=month)
    except ModelError:
        # custom date might be invalid
        abort(400)
    if post is None:
        abort(404)
    return render_template('post/post.html', post=post)


@post_bp.route('/post/<int:post_id>')
def render_post(post_id):
    post = PO.get_post(post_id)
    if post is None:
        abort(404)
    return redirect(url_for('post.render_post_by_permalink',
                            slug=post.slug,
                            year=post.created_year,
                            month=post.created_month))


@post_bp.route('/post/<int:post_id>/edit')
@admin_required
def edit_post(post_id):
    post = PO.get_post(post_id)
    if post is None:
        abort(404)
    return render_template('admin/compose.html', post=post)


@post_bp.route('/', methods=['POST'])
@admin_required
def create_post():              # todo: rename
    """
    Create a post from a draft.

    * admin required
    * required post data: slug, draft-id
    * optional post data: tags
    """
    slug = request.form.get('slug') or abort(400)
    tags = request.form.get('tags', '').split()
    draft_id = require_int(request.form.get('draft-id'), 400)
    draft = PO.get_draft(draft_id)
    author_id = session['uid']
    if draft is None:
        abort(404)
    try:
        # get title and text from draft
        post = Post(title=draft.title,
                    text=draft.text,
                    slug=slug,
                    author_id=author_id)
        PO.create_post(post)
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(url_for('post.prepare'))
    post.set_tags(tags)
    # create successfully, then delete draft
    PO.delete_draft(draft)
    return redirect(url_for('post.render_post_by_permalink',
                            slug=post.slug,
                            year=post.created_year,
                            month=post.created_month))


@post_bp.route('/post/<int:post_id>', methods=['POST'])
@admin_required
def update_post(post_id):
    """
    Update the post from draft.

    * admin required
    * required post data: post-id, draft-id
    * optional post data: tags, slug
    """
    post = PO.get_post(post_id)
    if post is None:
        abort(404)
    # assign title and text in draft to post
    draft = PO.get_draft(require_int(request.form.get('draft-id'), 400))
    if draft is None:
        abort(400)
    try:
        post.title = draft.title
        post.text = draft.text
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(url_for('post.edit_post', post_id=post.id))
    # handle slug
    slug = request.form.get('slug')
    if slug:
        try:
            post.slug = slug
        except ModelError as err:
            flash(err.message, category='error')
            return redirect(url_for('post.prepare'))
    # handle tags
    tags = request.form.get('tags')
    if tags:
        post.set_tags(tags.split())
    PO.delete_draft(draft)
    return redirect(url_for('post.render_post_by_permalink',
                            slug=post.slug,
                            year=post.created_year,
                            month=post.created_month))


@post_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    post = PO.get_post(post_id)
    if post is None:
        abort(404)
    PO.delete_post(post)
    return redirect(url_for('post.render_posts'))


def try_slugify(title, start=0, delim=u'-'):
    """ get a unique slug """
    suffix = start
    while True:
        if suffix > start:
            slug = slugify('%s%s%d' % (title, delim, suffix), delim)
        else:
            slug = slugify(title)
        post = PO.get_post_by_permalink(slug)
        if post is None:
            return slug
        suffix += 1


@post_bp.route('/prepare', methods=['POST', 'GET'])
@admin_required
def prepare():
    """
    Create or update a draft, and a fake post for previewing.
    The draft is used for updating or creating post later.

    * admin required
    * required post data: title, text
    * optional post data: draft-id, post-id
    """
    if request.method == 'POST':
        # required
        title = request.form.get('title')
        text = request.form.get('text')
        # optional
        draft_id = request.form.get('draft-id')
        post_id = request.form.get('post-id')

        if post_id is not None:
            post_id = require_int(post_id, 400)
            post = PO.get_post(post_id)
            if post is None:
                abort(400)
            if post.draft:
                ######## editing a post with draft saved
                draft = post.draft
                draft.title, draft.text = title, text
                PO.update_draft(draft)
            else:
                ######## editing a post
                draft = Draft(title, text)
                draft.post = post
                PO.create_draft(draft)

        elif draft_id is not None:
            ######## editing a draft
            draft_id = require_int(draft_id, 400)
            draft = PO.get_draft(draft_id)
            if draft is None:
                abort(400)
            draft.title, draft.text = title, text
            PO.update_draft(draft)
        else:
            ######## editing a scratch
            draft = Draft(title, text)
            PO.create_draft(draft)

    elif request.method == 'GET':
        # always show the most recently saved draft
        draft = PO.get_drafts(limit=1)
        if len(draft):
            draft = draft[0]
        else:
            abort(404)
        title = draft.title
        text = draft.text

    # get slug
    if draft.post:
        slug = draft.post.slug
    else:
        # todo: analysis tags from title and text
        slug = try_slugify(title)  # todo: use id as init value

    # make a fake post for previewing
    fake_post = None
    try:
        # created date and updated date are required
        fake_post = Post(title=title, text=text,
                         slug=slug, author_id=session['sid'])
        fake_post.created_at = datetime.utcnow()
        fake_post.updated_at = datetime.utcnow()
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(request.referrer or url_for('.render_posts'))

    # a fake post with id means updating this post instead of creating a new post
    if draft.post:
        fake_post.id = draft.post.id

    return render_template('post/preview.html', post=fake_post, draft=draft)


@post_bp.route('/draft/<int:draft_id>/edit')
@admin_required
def edit_draft(draft_id):
    draft = PO.get_draft(draft_id)
    if draft is None:
        abort(404)
    if draft.post is not None:
        return redirect(url_for('post.edit_post', post_id=draft.post.id))
    else:
        return render_template('admin/compose.html', draft=draft)


@post_bp.route('/drafts/', methods=['POST'])
@admin_required
def create_draft():
    title = request.form.get('title')
    text = request.form.get('text')
    post_id = request.form.get('post-id')
    try:
        draft = Draft(title, text)
    except ModelError as err:
        flash(err.message, category='error')
        return redirect(url_for('admin.compose'))
    post = None
    if post_id is not None:
        post = PO.get_post(require_int(post_id, 400))
    if post:
        draft.post = post
    PO.create_draft(draft)      # todo: rename create_draft to add_draft
    return redirect(url_for('.edit_draft', draft_id=draft.id))


@post_bp.route('/draft/<int:draft_id>', methods=['POST'])  # todo: use PUT
@admin_required
def update_draft(draft_id):
    draft = PO.get_draft(draft_id)
    if draft is None:
        abort(404)
    draft.title = request.form.get('title')
    draft.text = request.form.get('text')
    PO.update_draft(draft)
    return redirect(url_for('post.edit_draft', draft_id=draft.id))
