# -*- coding: utf-8 -*-

__all__ = ['Draft', 'Post', 'Tag', 'PostOperator']

from datetime import datetime
from sqlalchemy.schema import Index
from sqlalchemy.sql import and_
from sqlalchemy import (Column, String, Integer, Table,
                        DateTime, func, ForeignKey, desc)
from sqlalchemy.orm import (relationship, validates, backref, object_session)

from ..helpers import validate_slug, get_date_range, markdown
from . import Base, ModelError


post_tag_table = Table('_post_tag', Base.metadata,
                       Column('post_id', Integer, ForeignKey('post.id')),
                       Column('tag_id', Integer, ForeignKey('tag.id')))
post_readers_table = Table('_post_readers', Base.metadata,
                           Column('post_id', Integer, ForeignKey('post.id')),
                           Column('user_id', Integer, ForeignKey('user.id')))


class PostError(ModelError):
    def __init__(self, message):
        ModelError.__init__(self, message, model='Post')


class PostContent(Base):
    __tablename__ = 'post_content'
    id = Column(Integer, primary_key=True)
    content = Column(String)

    def __init__(self, content):
        self.content = content


class PostText(Base):
    __tablename__ = 'post_text'
    id = Column(Integer, primary_key=True)
    text = Column(String)

    def __init__(self, text):
        self.text = text


def lower_set(items):
    return set(item.lower() for item in items)


class Post(Base):
    __tablename__ = 'post'

    STATUS_PUBLIC = 0             # public post
    STATUS_PRIVATE = 1            # private post
    STATUS_TRASH = 2              # trash

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    slug = Column('slug', String, nullable=False, index=True)
    status = Column('status', Integer, nullable=False, default=0)
    created_at = Column('created_at', DateTime,
                        nullable=False,
                        default=func.now())
    updated_at = Column('updated_at', DateTime,
                        onupdate=func.now())
    version = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    ################ text ################
    text_id = Column(Integer, ForeignKey('post_text.id'))
    _text = relationship('PostText', uselist=False, backref='post')

    @property
    def text(self):
        if self._text:
            return self._text.text
        else:
            return None

    @text.setter
    def text(self, new_text):
        """Set text and convert text to HTML."""
        self.version += 1
        if new_text is None:
            self._text = None
            self._content = None
        else:
            if self._text:
                self._text.text = new_text
            else:
                self._text = PostText(new_text)
            if self._content:
                self._content.content = markdown(new_text)
            else:
                self._content = PostContent(markdown(new_text))

    ################ content ################
    content_id = Column(Integer, ForeignKey('post_content.id'))
    _content = relationship('PostContent', uselist=False, backref='post')

    @property
    def content(self):
        if self._content:
            return self._content.content
        else:
            return None

    ################ readers ################
    _readers = relationship('User', secondary=post_readers_table,
                            backref='posts')

    @property
    def readers(self):
        return self._readers

    @readers.setter
    def readers(self, new_readers):
        self.status = Post.STATUS_PRIVATE
        self._readers = new_readers

    ################ tags ################
    _tags = Column('tags', String)

    @property
    def tags(self):
        if self._tags:
            return self._tags.split()
        else:
            return []

    _tagobjs = relationship('Tag', secondary=post_tag_table,
                            back_populates='posts')

    def set_tags(self, names, nocommit=False):
        session = object_session(self)
        if session is None:
            raise RuntimeError('%s must be persistent' % self)
        to_remove = [name for name in self.tags
                     if name.lower() not in lower_set(names)]
        to_add = [name for name in set(names)
                  if name.lower() not in lower_set(self.tags)]
        removed_tags, added_tags = (self.remove_tags(to_remove, nocommit=True),
                                    self.add_tags(to_add, nocommit=True))
        if not nocommit:
            session.commit()
        return removed_tags, added_tags

    def add_tags(self, names, nocommit=False):
        session = object_session(self)
        if session is None:
            raise RuntimeError('%s must be persistent' % self)

        def _remove_duplicates(result, item):
            if item.lower() in lower_set(result):
                return result
            else:
                return result + [item]

        # remove duplicates (case insensitive)
        names = reduce(_remove_duplicates, [[]] + list(set(names)))
        # tags to add
        to_add = [name for name in names
                  if name.lower() not in lower_set(self.tags)]
        if len(to_add) == 0:
            return []
        # tags that exist in the database
        existings = session.query(Tag)\
            .filter(func.lower(Tag.name)\
            .in_(lower_set(to_add)))\
            .all()
        # tags that are going to be created
        to_create = [name for name in to_add
                     if name.lower() not in
                     [tag.name.lower() for tag in existings]]
        to_add = existings + [Tag(name) for name in to_create]
        self._tagobjs += to_add
        self._tags = ' '.join(tag.name for tag in self._tagobjs)
        if not nocommit:
            session.commit()
        return to_add

    def remove_tags(self, names, nocommit=False):
        session = object_session(self)
        if session is None:
            raise RuntimeError('%s must be persistent' % self)
        # get the tags that will be remove from this post
        to_remove = [tag for tag in self._tagobjs
                     if tag.name.lower() in lower_set(names)]
        if len(to_remove) == 0:
            return []
        # get the tags that will be deleted, are those
        # that only tag this post and will be removed
        to_delete = session.query(Tag)\
            .select_from(post_tag_table)\
            .join(Tag)\
            .filter(func.lower(Tag.name)\
            .in_(tag.name.lower() for tag in to_remove))\
            .group_by(Tag.id)\
            .having(func.count(Tag.id) == 1)\
            .all()
        # remove tags from post
        self._tagobjs = [tag for tag in self._tagobjs if tag not in to_remove]
        self._tags = ' '.join(tag.name for tag in self._tagobjs)
        # delete tags from database
        for tag in to_delete:
            session.delete(tag)
        if not nocommit:
            session.commit()
        return to_remove

    def clear_tags(self, nocommit=False):
        removed_tags = self.remove_tags(self.tags, nocommit)
        return removed_tags

    __table_args__ = (Index('post_slug_date', 'slug', 'created_at'),
                      Index('post_status', 'status'))

    def __init__(self, title, text, slug, author_id):
        self.version = 0
        self.title = title
        self.slug = slug
        self.created_at = None
        self.updated_at = None
        self.status = 0
        self.text = text
        self.author_id = author_id

    def __repr__(self):
        return '<Post:%d/%d/%s>' % (self.created_year,
                                    self.created_month,
                                    self.slug)

    @validates('slug')
    def validate_slug(self, _, slug):
        if not validate_slug(slug):
            raise PostError('invalid slug')
        return slug

    @property
    def created_year(self):
        if self.created_at is None:
            return datetime.utcnow().year
        else:
            return self.created_at.year

    @property
    def created_month(self):
        if self.created_at is None:
            return datetime.utcnow().month
        else:
            return self.created_at.month

    @staticmethod
    def generate_permalink(slug, year=None, month=None):
        if year is None:
            year = datetime.utcnow().year
        if month is None:
            month = datetime.utcnow().month
        if slug:
            return '%d/%d/%s' % (year, month, slug)
        else:
            raise PostError('slug is empty')

    @property
    def permalink(self):
        return Post.generate_permalink(self.slug,
                                       self.created_year,
                                       self.created_month)

    def as_dict(self, meta=False):
        post_dict = {}
        exclude = ('metadata', 'draft', 'content_id', 'text_id')
        for key in dir(self):
            if key.isupper():
                continue
            if key.startswith('_'):
                continue
            if key in exclude:
                continue
            if meta and key in ('text', 'content'):
                continue
            value = getattr(self, key)
            if not hasattr(value, '__call__'):
                post_dict[key] = value
        return post_dict


class DraftError(ModelError):
    def __init__(self, message):
        ModelError.__init__(self, message, model='Draft')


class Draft(Base):
    __tablename__ = 'draft'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    title = Column(String)
    text = Column(String)
    saved_at = Column(DateTime,
                      nullable=False,
                      onupdate=func.now(),
                      default=func.now())
    publish_at = Column(DateTime)
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship("Post", backref=backref("draft", uselist=False))

    def __init__(self, title=None, text=None,
                 post_id=None,
                 saved_at=None,
                 publish_at=None):
        self.title = title
        self.text = text
        self.post_id = post_id
        self.saved_at = saved_at
        self.publish_at = publish_at


class TagError(ModelError):
    def __init__(self, message):
        ModelError.__init__(self, message, model='Tag')


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    posts = relationship('Post',
                         secondary=post_tag_table,
                         back_populates='_tagobjs')

    def __init__(self, name):
        self.name = name

    @validates('name')
    def validate_name(self, _, name):
        for c in '\t\n\r +':
            if c in name:
                raise TagError('invalid tag name')
        return name

    def __repr__(self):
        return '<Tag:%s>' % self.name

    def __str__(self):
        return self.name


class PostOperator(object):
    def __init__(self, session=None):
        self.session = session

    def get_tag(self, name):
        return self.session.query(Tag).filter_by(name=name).first()

    def get_public_tags(self):
        return self.session.query(Tag)\
            .select_from(post_tag_table)\
            .join(Tag).join(Post)\
            .filter(Post.status == Post.STATUS_PUBLIC)

    def get_private_tags(self):
        return self.session.query(Tag)\
            .select_from(post_tag_table)\
            .join(Tag).join(Post)\
            .filter(Post.status == Post.STATUS_PRIVATE)

    def get_trash_tags(self):
        return self.session.query(Tag)\
            .select_from(post_tag_table)\
            .join(Tag).join(Post)\
            .filter(Post.status == Post.STATUS_TRASH)

    def update_tag(self, tag):
        """ update tag """
        self.session.commit()
        return tag

    def delete_tag(self, tag):
        self.session.delete(tag)
        self.session.commit()

    def get_post(self, post_id):
        """ return a Post object or None """
        return self.session.query(Post).get(post_id)

    def get_post_by_permalink(self, slug, year=None, month=None):
        now = datetime.utcnow()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        start, end = get_date_range(year, month)
        return self.session.query(Post)\
            .filter(and_(Post.created_at >= start,
                         Post.created_at < end,
                         Post.slug == slug)).first()

    def query_posts(self, status, offset=0, limit=20,
                    tags=None, date=None, sort=None, asc=False):
        q = self.session.query(Post)
        # filter posts that match all tags
        # see: http://www.simple-talk.com/sql/t-sql-programming/divided-we-stand-the-sql-of-relational-division/
        if tags:
            q = q.select_from(post_tag_table).join(Post).join(Tag)\
                .filter(Tag.name.in_(tags))\
                .group_by(Post.id)\
                .having(func.count(Post.id) == len(tags))
        if date:
            q = q.filter(and_(Post.created_at >= date[0],
                              Post.created_at < date[1]))
        # sort posts by which column
        if sort is None:
            sort = 'created_at'
        if (not isinstance(sort, basestring)) or (not hasattr(Post, sort)):
            raise ModelError('invalid sort key')
        # Post id column is considered when sorting the created_at column,
        # this is because when you create for example many posts at the
        # same time (i.e. in one second), the posts with the same created
        # time will not be listed in create time order, this is not what
        # we expect. so post id column is taken into account to make it in order
        columns_to_sort = [sort if asc else desc(sort)]
        if sort == 'created_at':
            columns_to_sort.append(Post.id if asc else desc(Post.id))
        # filter posts that only in which statuses
        if isinstance(status, int):
            q = q.filter(Post.status == status)
        else:
            q = q.filter(Post.status.in_(status))
        if limit is None:
            # limit set to None means get all posts
            posts = q.order_by(*columns_to_sort).offset(offset).all()
            more = False
        else:
            # always fetch limit+1 posts to indicate if there are more posts left
            posts = q.order_by(*columns_to_sort).offset(offset).limit(limit + 1).all()
            more = len(posts) > limit
            posts = posts[:limit]
        return posts, more

    def get_public_posts(self, **kwargs):
        return self.query_posts(Post.STATUS_PUBLIC, **kwargs)

    def get_private_posts(self, **kwargs):
        return self.query_posts(Post.STATUS_PRIVATE, **kwargs)

    def get_posts(self, **kwargs):
        return self.query_posts([Post.STATUS_PRIVATE, Post.STATUS_PUBLIC],
                                **kwargs)

    def get_trashed_posts(self, **kwargs):
        return self.query_posts(Post.STATUS_TRASH, **kwargs)

    def update_post(self, post):
        self.session.commit()
        return post

    def create_post(self, post):
        if self.get_post_by_permalink(post.slug):
            raise ModelError('slug is not unique')
        self.session.add(post)
        self.session.commit()
        return post

    def trash_post(self, post):
        post.status = Post.STATUS_TRASH
        self.session.commit()
        return post

    def publish_post(self, post):
        post.status = Post.STATUS_PUBLIC
        self.session.commit()
        return post

    def hide_post(self, post):
        post.status = Post.STATUS_PRIVATE
        self.session.commit()
        return post

    def delete_post(self, post):
        post.clear_tags(nocommit=True)  # don't commit
        self.session.delete(post)
        self.session.commit()
        return post

    def delete_posts(self, posts):
        for post in posts:
            post.clear_tags(nocommit=True)
            self.session.delete(post)
        self.session.commit()
        return posts

    def get_draft(self, id):
        return self.session.query(Draft).get(id)

    def get_post_draft(self, post):
        return self.session.query(Post)\
            .filter_by(post_id=post.id).first()

    def get_drafts(self, offset=0, limit=20):
        return self.session.query(Draft)\
            .order_by(desc(Draft.saved_at))\
            .offset(offset).limit(limit).all()

    def create_draft(self, draft):
        self.session.add(draft)
        self.session.commit()
        return draft

    def update_draft(self, draft):
        self.session.commit()
        return draft

    def delete_draft(self, draft):
        self.session.delete(draft)
        self.session.commit()
