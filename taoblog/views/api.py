from flask import (Blueprint, current_app as app,
                   g, request, make_response,
                   jsonify, session)

from ..models import ModelError, Session
from ..models.post import Post, Draft, PostOperator
from .helpers import (require_int, JumpDirectly)


BP = Blueprint('api', __name__)
PO = PostOperator(Session())


def get_plain_dict(post, meta):
    post_dict = post.as_dict(meta)
    if 'created_at' in post_dict:
        post_dict['created_at'] = post_dict['created_at'] and \
            unicode(post_dict['created_at'])
    if 'updated_at' in post_dict:
        post_dict['updated_at'] = post_dict['updated_at'] and \
            unicode(post_dict['updated_at'])
    return post_dict


def jsonify_error(message, status):
    return make_response(
        jsonify({'stat': 'fail',
                 'message': message}),
        status)


def jsonify_posts(posts, meta=False, **kwargs):
    response = kwargs
    response.update({'posts': [get_plain_dict(post, meta) for post in posts],
                     'total_posts': len(posts)})
    return jsonify({'stat': 'ok',
                    'response': response})


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
                raise JumpDirectly(jsonify_error('admin required', 403))
        elif status == 'trash':
            status_code.append(Post.STATUS_TRASH)
            if not g.is_admin:
                raise JumpDirectly(jsonify_error('admin required', 403))
        else:
            raise JumpDirectly(jsonify_error('invalid status', 400))
    if len(status_code) == 0:
        raise JumpDirectly(jsonify_error('status not found', 400))
    return status_code


@BP.route('/drafts/', methods=['DELETE'])
def delete_drafts():
    if not g.is_admin:
        return jsonify_error('admin required', 403)
    ids = [require_int(id, JumpDirectly(jsonify_error('invalid draft id', 400)))
           for id in request.args.get('bulk', '').split(',') if id.strip()]
    if len(ids) > 0:
        deleted_rows = PO.session.query(Draft).\
            filter(Draft.id.in_(ids)).\
            delete(synchronize_session='fetch')
        PO.session.commit()
    else:
        deleted_rows = 0
    return jsonify({'stat': 'ok', 'response': {'total_drafts': deleted_rows}})


@BP.route('/posts/', methods=['DELETE'])
def delete_posts():
    """
    Delete posts from server.

    * admin required
    * optional arguments: bulk, status

    bulk is a list of post IDs separated by comma.
    """
    if not g.is_admin:
        return jsonify_error('admin required', 403)
    posts = []
    # get posts from post IDs
    ids = [require_int(id, JumpDirectly(jsonify_error('invalid post id', 400)))
           for id in request.args.get('bulk', '').split(',') if id.strip()]
    if len(ids) > 0:
        posts = PO.session.query(Post).filter(Post.id.in_(ids)).all()
    # get all posts in specified status
    status = request.args.get('status')
    if status:
        status_code = get_status_code(status)
        posts += PO.session.query(Post).\
            filter(Post.status.in_(status_code)).all()
    # delete all of them
    if len(posts) > 0:
        PO.delete_posts(posts)
    return jsonify({'stat': 'ok', 'response': {'total_posts': len(posts)}})


@BP.route('/posts/', methods=['POST'])
def create_post():
    """
    Create a post. Return the post.

    * admin required
    * required post data: title, slug
    * optional post data: text, tags, private
    """
    if not g.is_admin:
        return jsonify_error('admin required', 403)
    title = request.form.get('title')
    if not title:
        return jsonify_error('title required', 400)
    slug = request.form.get('slug')
    if not slug:
        return jsonify_error('slug required', 400)
    post = PO.get_post_by_permalink(slug)
    if post is not None:
        return jsonify_error('slug is not unique', 400)
    private = bool(request.form.get('private', False))
    text = request.form.get('text')
    tags = request.form.get('tags')
    author_id = session['uid']
    if tags:
        tags = tags.split()
    try:
        post = Post(title=title, text=text,
                    slug=slug, author_id=author_id)
        if private:
            post.status = Post.STATUS_PRIVATE
        PO.create_post(post)
        if tags:
            post.set_tags(tags)
    except ModelError as err:
        return jsonify_error(err.message, 400)
    return jsonify_posts([post])


@BP.route('/posts/')
def get_posts():
    """
    Get posts.

    * admin required
    * arguments: offset, limit, status, meta, sort, asc, tags, id
    """
    offset = require_int(request.args.get('offset', 0),
                         JumpDirectly(jsonify_error('invalid offset', 400)))
    limit = require_int(
        request.args.get('limit', app.config['POST_API_PERPAGE']),
        JumpDirectly(jsonify_error('invalid limit', 400)))
    status = request.args.get('status', 'public+private').lower()
    # admin may be required in this function
    status_code = get_status_code(status)
    meta = 'meta' in request.args
    sort = request.args.get('sort', 'created_at')
    # if asc argument is found, do asc sort
    asc = 'asc' in request.args
    tags = request.args.get('tags')
    id = request.args.get('id')
    if id is None:
        # get multi posts
        try:
            posts, more = PO.query_posts(
                status=status_code, offset=offset, limit=limit,
                tags=tags and tags.split('+'),
                date=None, sort=sort, asc=asc)
        except ModelError as err:
            return jsonify_error(err.message, 400)
    else:
        # get single post when post id is specified
        more = False
        id = require_int(id, JumpDirectly(jsonify_error('invalid id', 400)))
        post = PO.get_post(id)
        if post is None:
            return jsonify_error('post not found', 404)
        else:
            if not g.is_admin and (post.status in (Post.STATUS_PRIVATE,
                                                   Post.STATUS_TRASH)):
                return jsonify_error('admin required', 403)
            posts = [post]
    return jsonify_posts(posts, meta, more=more)


def set_status(status):
    """
    Set post status (publish, hide, or trash post)

    * admin required
    * required arguments: id, or id list
    """
    if not g.is_admin:
        return jsonify_error('admin required', 403)
    if status not in [Post.STATUS_TRASH, Post.STATUS_PUBLIC, Post.STATUS_PRIVATE]:
        return jsonify_error('invalid status', 400)
    id_param = request.form.get('id')
    if id_param is None:
        return jsonify_error('invalid id parameter', 400)
    id_list = [require_int(id, JumpDirectly(jsonify_error('invalid id', 400)))
               for id in id_param.split(',')]
    posts = PO.session.query(Post).filter(Post.id.in_(id_list)).all()
    for post in posts:
        post.status = status
    PO.session.commit()
    return jsonify_posts(posts, meta=True)


@BP.route('/posts/trash', methods=['POST'])
def trash_posts():
    return set_status(Post.STATUS_TRASH)


@BP.route('/posts/publish', methods=['POST'])
def publish_posts():
    return set_status(Post.STATUS_PUBLIC)


@BP.route('/posts/hide', methods=['POST'])
def hide_posts():
    return set_status(Post.STATUS_PRIVATE)
