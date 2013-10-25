__all__ = ['TestPost', 'TestDraft', 'TestTag', 'TestPostOperator']

import time
import unittest
from datetime import datetime

from taoblog.tests.helpers import TaoblogTestCase
from taoblog.models.post import Post, PostText, PostOperator, Tag, Draft
from taoblog.models import ModelError


class TestTag(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_name(self):
        self.assertRaises(ModelError, Tag, 'hello world')
        self.assertRaises(ModelError, Tag, 'hello\tworld')
        self.assertRaises(ModelError, Tag, 'hello\nworld')
        self.assertRaises(ModelError, Tag, 'hello\rworld')
        self.assertRaises(ModelError, Tag, 'hello+world')


class TestDraft(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_autoupdate(self):
        draft = Draft(title='title', text='text')
        self.session.add(draft)
        self.session.commit()
        self.assertIsNotNone(draft.saved_at)
        old_date = draft.saved_at

        draft.title = 'new title'
        time.sleep(1)
        self.session.commit()
        self.assertTrue(draft.saved_at>old_date)


class TestPost(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_slug(self):
        post = Post('hello world', 'world', 'hello-world')
        self.assertEqual(post.slug, 'hello-world')

        # invalid slug
        def _set_slug(slug):
            post.slug = slug
        self.assertRaises(ModelError, _set_slug, 'this contains spaces')
        self.assertRaises(ModelError, _set_slug, 'this-contains-newline\n')
        self.assertRaises(ModelError, _set_slug, 'this-contains-newline\r')
        self.assertRaises(ModelError, _set_slug, 'this-contains/slash')
        self.assertRaises(ModelError, _set_slug, 'this-contains-?')
        self.assertRaises(ModelError, _set_slug, '')
        self.assertRaises(ModelError, _set_slug, ' ')
        self.assertRaises(ModelError, _set_slug, '\t')

        self.assertEqual(post.permalink, '%d/%d/%s' % (datetime.utcnow().year,
                                                       datetime.utcnow().month,
                                                       post.slug))

    def test_date(self):
        post = Post('hello world', 'world', 'hello-world')
        self.assertIsNone(post.created_at)
        self.assertIsNone(post.updated_at)
        self.session.add(post)
        self.session.commit()
        self.assertIsNotNone(post.created_at)
        self.assertIsNone(post.updated_at)
        post.text = 'new world'
        self.session.commit()
        self.assertIsNotNone(post.updated_at)

    def test_tag(self):
        clojure = Post('clojure lisp', '', 'clojure-lisp')
        scheme = Post('scheme lisp', '', 'scheme-lisp')
        # post not added to session, raise error
        self.assertRaises(RuntimeError, clojure.add_tags, ['clojure'])
        self.assertRaises(RuntimeError, clojure.remove_tags, ['clojure'])
        self.assertRaises(RuntimeError, clojure.set_tags, ['clojure'])
        self.assertRaises(RuntimeError, clojure.clear_tags)
        self.session.add(clojure)
        self.session.add(scheme)
        # add tags
        # post     tags
        # clojure: Clojure, LISP
        # scheme:  Scheme, LISP
        self.assertEqual(clojure.add_tags(['Clojure'])[0].name, 'Clojure')
        self.assertEqual(clojure.add_tags(['LISP'])[0].name, 'LISP')
        self.assertEqual(set(clojure.tags), {'Clojure', 'LISP'})
        self.assertEqual(scheme.add_tags(['Scheme'])[0].name, 'Scheme')
        self.assertEqual(scheme.add_tags(['SCHEME']), []) # no new tag added
        self.assertEqual(scheme.add_tags(['scheme']), []) # no new tag added
        self.assertEqual(scheme.add_tags(['lisp'])[0].name, 'LISP')
        self.assertEqual(set(scheme.tags), {'Scheme', 'LISP'})
        self.assertEqual(set(clojure.tags), {'Clojure', 'LISP'})
        # remove tags
        scheme.remove_tags(['SCHEME'])
        self.assertIsNone(self.session.query(Tag).filter_by(name='Scheme').first())
        scheme.remove_tags(['lisp'])
        self.assertEqual(self.session.query(Tag).filter_by(name='LISP').first().name, 'LISP')
        self.assertEqual(scheme.tags, [])
        # clear tags
        clojure.clear_tags()
        self.assertEqual(clojure.tags, [])
        self.assertIsNone(self.session.query(Tag).filter_by(name='Clojure').first())
        self.assertIsNone(self.session.query(Tag).first())
        scheme.set_tags(['SCHEME', 'LISP', 'Scheme', 'Lisp'])
        self.assertEqual(set(tag.name for tag in self.session.query(Tag).all()), {'SCHEME', 'LISP'})
        self.assertEqual(scheme.set_tags(['scheme', 'lisp', 'scheme', 'lisp']), ([], [])) # add none, remove none

    def test_content(self):
        post = Post('hello world', 'world', 'hello-world')
        self.assertEqual(post.content, '<p>%s</p>\n' % post.text)
        post.text = 'new world'
        self.assertEqual(post.content, '<p>%s</p>\n' % post.text)

    def test_query(self):
        post = Post(title='a title', text='the first post', slug='a-title')
        self.session.add(post)
        self.session.commit()
        result = self.session.query(Post).filter_by(title='a title').one()
        self.assertEqual(result.title, post.title)

        post = Post(title='a title', text='the second post', slug='a-title')
        self.session.add(post)
        self.session.commit()
        result = self.session.query(Post).join(PostText).filter(PostText.text=='the second post').one()
        self.assertEqual(result.text, post.text)

    def test_readers(self):
        post = Post(title='jim tao peter', text='the text', slug='jim-tao-peter')
        self.session.add(post)
        self.session.commit()
        from taoblog.models.user import User, UserOperator
        jim = User(name='Jim',
                   email='jim@aa.com',
                   provider='openid',
                   identity='jim')
        tao = User(name='Tao',
                   email='tao@aa.com',
                   provider='openid',
                   identity='tao')
        peter = User(name='Peter',
                     email='peter@aa.com',
                     provider='openid',
                     identity='peter')
        post.readers = [jim, tao, peter]
        self.assertEqual(post.status, Post.STATUS_PRIVATE)
        self.assertEqual(set(self.session.query(User).all()), {jim, tao, peter})
        post2 = Post(title='jim tao', text='text', slug='jim-tao')
        self.assertEqual(post2.status, Post.STATUS_PUBLIC)
        dude = User(name='Dude',
                    email='dude@aa.com',
                    provider='openid',
                    identity='dude')
        post2.readers = [jim, tao, dude]
        self.assertEqual(post2.status, Post.STATUS_PRIVATE)
        self.assertEqual(set(self.session.query(User).all()), {jim, tao, dude, peter})
        self.assertEqual(set(peter.posts), {post})
        self.assertEqual(set(jim.posts), {post, post2})
        self.assertEqual(set(dude.posts), {post2})
        playboy = User(name='Playboy',
                       email='play@aa.com',
                       provider='openid',
                       identity='playboy')
        self.session.add(playboy)
        self.assertEqual(playboy.posts, [])


class TestPostOperator(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_create_post(self):
        post = Post(title='hello', text='world', slug='hello')
        op = PostOperator(self.session)
        op.create_post(post)
        self.assertEqual(op.get_post(post.id), post)
        # same slug is not allowed
        another_post = Post(title='hello', text='world', slug='hello')
        self.assertRaises(ModelError, op.create_post, another_post)

    def test_get_posts(self):
        op = PostOperator(self.session)
        # create post
        post = Post(title='hello', text='world', slug='hello-world')
        op.create_post(post)
        self.assertEqual(op.get_post(post.id), post)
        # get public posts
        haskell = Post(title='haskell-2012', text='world3', slug='hehe')
        haskell.created_at = datetime(year=2012, month=4, day=29)
        op.create_post(haskell)
        haskell.add_tags(['haskell', 'fp'])

        scheme = Post(title='scheme-2010', text='world2', slug='haha')
        scheme.created_at = datetime(year=2010, month=1, day=16)
        op.create_post(scheme)
        scheme.add_tags(['scheme', 'fp'])

        clojure = Post(title='clojure-2009', text='world1', slug='haha')
        clojure.created_at = datetime(year=2009, month=12, day=13)
        op.create_post(clojure)
        clojure.add_tags(['clojure', 'fp'])
        posts, more = op.get_public_posts()
        self.assertEqual(4, len(posts))
        self.assertEqual(posts, [post, haskell, scheme, clojure])
        self.assertFalse(more)  # no more
        self.assertEqual(set([str(tag) for tag in op.get_public_tags()]),
                         {'clojure', 'fp', 'scheme', 'haskell'})

        op.trash_post(post)
        posts, more = op.get_public_posts()
        self.assertEqual(posts, [haskell, scheme, clojure])
        self.assertFalse(more)
        # scheme will be removed from public tags
        op.trash_post(scheme)
        self.assertEqual(set([tag.name for tag in op.get_public_tags()]),
                         {'clojure', 'fp', 'haskell'})
        self.assertEqual(set([str(tag) for tag in op.get_trash_tags()]),
                         {'scheme', 'fp'})


if __name__ == '__main__':
    unittest.main()
