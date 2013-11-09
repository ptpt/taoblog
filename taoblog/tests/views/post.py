import unittest

import taoblog
from taoblog.tests.helpers import TaoblogTestCase


class PostViewTestCase(TaoblogTestCase):
    def setUp(self):
        self.db_setup()
        self.app = taoblog.application.test_client()

    def tearDown(self):
        self.db_teardown()

    def login(self):
        data = {'name': 'Admin',
                'provider': 'openid',
                'identity': 'a secret',
                'email': 'admin@gmail.com',
                'sid': 'sid'}
        return self.app.post('/login/testing', data=data)

    def logout(self):
        return self.app.post('/logout/tesing', data={'sid': 'sid'})

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
        self.login()
        rv = self.app.get('/admin/')
        self.assertEqual(rv.status_code, 200)

        # create draft
        rv = self.app.post('/prepare', data={'title': 'this is a title',
                                             'text': 'this is a text'})
        self.assertEqual(rv.status_code, 200)

        # success: create post from draft
        rv = self.app.post('/', data={'draft-id': 1,
                                      'slug': 'hello'})
        self.assertEqual(rv.status_code, 302)
        self.assertTrue(rv.location.endswith('/hello'))

        # fail: draft with id 1 has been deleted
        rv = self.app.post('/', data={'draft-id': 1,
                                      'slug': 'hello-2'})
        self.assertEqual(rv.status_code, 404)

        # fail: duplicated slug
        rv = self.app.post('/prepare', data={'title': 'this is a title',
                                             'text': 'this is a text'})
        rv = self.app.post('/', data={'draft-id': 1,
                                      'slug': 'hello'})
        # it should redirect to a page with error info
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(rv.location, 'http://localhost/prepare')

        # fail: draft-id is invalid
        rv = self.app.post('/', data={'draft-id': 'invalid-number',
                                      'slug': 'slug'})
        self.assertEqual(rv.status_code, 400)

        # fail: slug is missing
        rv = self.app.post('/', data={'draft-id': 2})
        self.assertEqual(rv.status_code, 400)

        # fail: draft-id is missing
        rv = self.app.post('/', data={'slug': 'slug'})
        self.assertEqual(rv.status_code, 400)


if __name__ == '__main__':
    unittest.main()
