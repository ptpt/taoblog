import json
from datetime import date

from ..helpers import TaoblogTestCase
try:
    from html import escape as html_escape
except ImportError:
    from cgi import escape as html_escape


class PostViewTestCase(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_feed(self):
        rv = self.app.get('/feed/')
        self.assertEqual(rv.status_code, 200)
        perpage = self.app.application.config['POST_FEED_PERPAGE']
        title = '<h1>This</h1> is Title {0}'
        text = '<span>this</span> is text {0}'
        slug = 'this-is-slug-{0}'
        self.login_as_admin()
        for n in range(perpage + 3, 0, -1):
            self.add_post(title=title.format(n),
                          text=text.format(n),
                          slug=slug.format(n))
        user = self.logout()
        author_name = user['name']
        rv = self.app.get('/feed/')
        self.assertEqual(rv.status_code, 200)
        # make sure it renders the first POST_FEED_PERPAGE posts only
        for n in range(perpage + 3, 0, -1):
            if n <= perpage:
                self.assertIn(html_escape(title.format(n)), rv.data)
                self.assertIn(html_escape(text.format(n)), rv.data)
                self.assertIn(slug.format(n), rv.data)
                self.assertIn(author_name, rv.data)
            else:
                self.assertNotIn(html_escape(title.format(n)), rv.data)
                self.assertNotIn(html_escape(text.format(n)), rv.data)
                self.assertNotIn(slug.format(n), rv.data)

    def test_render_posts_and_archive(self):

        def assert_get(path):
            posts_resp = self.app.get(path)
            self.assertEqual(posts_resp.status_code, 200)
            archive_resp = self.app.get('/archive' + path)
            self.assertEqual(archive_resp.status_code, 200)
            return posts_resp, archive_resp

        assert_get('/')

        perpage = self.app.application.config['POST_PERPAGE']
        title = '<h1>This</h1> is Title {0}'
        text = '<span>this</span> is text {0}'
        slug = 'this-is-slug-{0}'

        self.login_as_admin()
        for n in range(perpage * 2, 0, -1):
            tags = ' '.join(['first_page' if n <= perpage else 'second_page',
                             'even' if n % 2 == 0 else 'odd'])
            self.add_post(title=title.format(n),
                          text=text.format(n),
                          slug=slug.format(n),
                          tags=tags)
        self.logout()

        def assert_in_resps(n, resps):
            posts_resp, archive_resp = resps
            self.assertIn(html_escape(title.format(n)), posts_resp.data)
            self.assertIn(text.format(n), posts_resp.data)
            self.assertIn(slug.format(n), posts_resp.data)
            self.assertIn(html_escape(title.format(n)), archive_resp.data)
            self.assertIn(slug.format(n), archive_resp.data)

        def assert_not_in_resps(n, resps):
            posts_resp, archive_resp = resps
            self.assertNotIn(html_escape(title.format(n)), posts_resp.data)
            self.assertNotIn(text.format(n), posts_resp.data)
            self.assertNotIn(slug.format(n), posts_resp.data)
            self.assertNotIn(html_escape(title.format(n)), archive_resp.data)
            self.assertNotIn(slug.format(n), archive_resp.data)

        today = date.today()
        year = today.year
        month = today.month
        rv = assert_get('/')
        date_1989_rv = assert_get('/1989/06/')
        date_now_rv = assert_get('/{year}/{month}/'.format(year=year, month=month))
        for n in range(1, perpage+1):
            assert_in_resps(n, rv)
            assert_in_resps(n, date_now_rv)
            assert_not_in_resps(n, date_1989_rv)

        rv = assert_get('/?page=2')
        date_1989_rv = assert_get('/1989/06/?page=2')
        date_now_rv = assert_get(
            '/{year}/{month}/?page=2'.format(year=year, month=month)
        )
        for n in range(perpage+1, perpage*2+1):
            assert_in_resps(n, rv)
            assert_in_resps(n, date_now_rv)
            assert_not_in_resps(n, date_1989_rv)

        odd_rv = assert_get('/tagged/odd/')
        even_rv = assert_get('/tagged/even/')
        second_even_rv = assert_get('/tagged/even+second_page/')
        date_1989_rv = assert_get('/tagged/even+second_page/1989/06/')
        date_now_rv = assert_get(
            '/tagged/even+second_page/{year}/{month}/'.format(year=year, month=month)
        )
        for n in range(1, perpage*2+1):
            assert_not_in_resps(n, date_1989_rv)
            if n <= perpage:
                rv = even_rv if n % 2 == 0 else odd_rv
                assert_in_resps(n, rv)
            elif n % 2 == 0:
                assert_in_resps(n, second_even_rv)
                assert_in_resps(n, date_now_rv)

    def test_render_post_by_permlink(self):
        title = 'This is Title'
        text = 'This is Text'
        slug = 'this-is-slug'
        self.login_as_admin()
        self.add_post(title=title, text=text, slug=slug)
        self.logout()
        today = date.today()
        rv = self.app.get('/{year}/{month}/{slug}'.format(year=today.year,
                                                          month=today.month,
                                                          slug=slug))
        self.assertEqual(rv.status_code, 200)
        self.assertIn(title, rv.data)
        self.assertIn(text, rv.data)
        self.assertIn(slug, rv.data)
        # not found
        rv = self.app.get('/1989/06/{slug}'.format(slug=slug))
        self.assertEqual(rv.status_code, 404)
        rv = self.app.get('/{year}/{month}/invalid-slug')
        self.assertEqual(rv.status_code, 404)
        rv = self.app.get('/2012/abcd/{slug}'.format(slug=slug))
        self.assertEqual(rv.status_code, 404)
        # request syntax error
        rv = self.app.get('/12/40/{slug}'.format(slug=slug))
        self.assertEqual(rv.status_code, 400)

    def test_render_post(self):
        rv = self.app.get('/post/1')
        self.assertEqual(rv.status_code, 404)
        title = 'This is Title'
        text = 'This is text'
        slug = 'this-is-slug'
        self.login_as_admin()
        rv = self.add_post(title=title, text=text, slug=slug)
        self.logout()
        post_id = json.loads(rv.data)['response']['posts'][0]['id']
        path = '/post/{id}'.format(id=post_id)
        rv = self.app.get(path)
        self.assertEqual(rv.status_code, 302)
        rv = self.app.get(path, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(title, rv.data)
        self.assertIn(text, rv.data)
        self.assertIn(slug, rv.data)

    def test_render_post_editing(self):
        rv = self.app.get('/post/1/edit')
        # admin required
        self.assertEqual(rv.status_code, 302)
        self.login_as_admin()
        rv = self.app.get('/post/1/edit')
        self.assertEqual(rv.status_code, 404)
        title = 'This is Title'
        text = 'This is text'
        slug = 'this-is-slug'
        rv = self.add_post(title=title, text=text, slug=slug)
        post_id = json.loads(rv.data)['response']['posts'][0]['id']
        path = '/post/{id}/edit'.format(id=post_id)
        rv = self.app.get(path)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(title, rv.data)
        self.assertIn(text, rv.data)

    def test_compose(self):
        # redirect to login
        rv = self.app.get('/admin/compose')
        self.assertEqual(rv.status_code, 302)
        rv = self.app.get('/admin/compose', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

        # success: login
        self.login_as_admin()
        rv = self.app.get('/admin/')
        self.assertEqual(rv.status_code, 200)

        # create draft
        rv = self.app.post('/prepare', data={'title': 'this is a title',
                                             'text': 'this is a text',
                                             'sid': 'sid'})
        self.assertEqual(rv.status_code, 200)

        # success: create post from draft
        rv = self.app.post('/', data={'draft-id': 1,
                                      'slug': 'hello',
                                      'sid': 'sid'})
        self.assertEqual(rv.status_code, 302)
        self.assertTrue(rv.location.endswith('/hello'))

        # fail: draft with id 1 has been deleted
        rv = self.app.post('/', data={'draft-id': 1,
                                      'slug': 'hello-2',
                                      'sid': 'sid'})
        self.assertEqual(rv.status_code, 404)

        # fail: duplicated slug
        rv = self.app.post('/prepare', data={'title': 'this is a title',
                                             'text': 'this is a text',
                                             'sid': 'sid'})
        rv = self.app.post('/', data={'draft-id': 1,
                                      'slug': 'hello',
                                      'sid': 'sid'})
        # it should redirect to a page with error info
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 'http://localhost/prepare')

        # fail: draft-id is invalid
        rv = self.app.post('/', data={'draft-id': 'invalid-number',
                                      'slug': 'slug',
                                      'sid': 'sid'})
        self.assertEqual(rv.status_code, 400)

        # fail: slug is missing
        rv = self.app.post('/', data={'draft-id': 2,
                                      'sid': 'sid'})
        self.assertEqual(rv.status_code, 400)

        # fail: draft-id is missing
        rv = self.app.post('/', data={'slug': 'slug',
                                      'sid': 'sid'})
        self.assertEqual(rv.status_code, 400)