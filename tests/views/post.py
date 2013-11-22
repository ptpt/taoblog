from ..helpers import TaoblogTestCase


class PostViewTestCase(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_home(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        rv = self.app.get('/archive/')
        self.assertEqual(rv.status_code, 200)
        rv = self.app.get('/not-found')
        self.assertEqual(rv.status_code, 404)

    def test_compose(self):
        self.logout()

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