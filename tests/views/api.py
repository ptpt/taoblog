import json

from ..helpers import TaoblogTestCase


class APIViewTestCase(TaoblogTestCase):
    def setUp(self):
        self.db_setup()

    def tearDown(self):
        self.db_teardown()

    def test_create_posts(self):
        api = '/api/posts/'
        # fail: admin required
        rv = self.client.post(api, data={'title': 'this is title',
                                         'slug': 'this is slug'})
        self.assertEqual(rv.status_code, 403)
        # fail: not admin
        self.login()
        rv = self.client.post(api, data={'title': 'this is title',
                                         'slug': 'this-is-slug'})
        self.assertEqual(rv.status_code, 403)
        self.logout()
        # sucess
        self.login_as_admin()
        rv = self.client.post(api, data={'title': 'this is title',
                                         'text': 'hello world',
                                         'slug': 'this-is-another-slug'})
        self.assertEqual(rv.status_code, 200)
        # fail: empty title
        rv = self.client.post(api, data={'title': '',
                                         'slug': 'slug'})
        self.assertEqual(rv.status_code, 400)
        # fail: empty slug
        rv = self.client.post(api, data={'title': 'this is title'})
        self.assertEqual(rv.status_code, 400)
        # success
        rv = self.client.post(api, data={'title': 'this is title',
                                         'slug': 'slug',
                                         'tags': 'python ruby this-is-cool'})
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertEqual(data['stat'], 'ok')
        self.assertEqual(data['response']['total_posts'], 1)
        self.assertEqual(data['response']['posts'][0]['title'], 'this is title')
        self.assertEqual(data['response']['posts'][0]['slug'], 'slug')
        self.assertIsNone(data['response']['posts'][0]['text'])
        self.assertEqual(set(data['response']['posts'][0]['tags']),
                         {'ruby', 'python', 'this-is-cool'})
        # fail: duplicated slug
        rv = self.client.post(api, data={'title': 'this is another title',
                                         'slug': 'slug'})
        self.assertEqual(rv.status_code, 400)
        # fail: invalid tags
        rv = self.client.post(api, data={'title': 'this is title',
                                         'slug': 'another-slug',
                                         'tags': 'this-is-invalid+'})
        self.assertEqual(rv.status_code, 400)

    def test_get_posts(self):
        api = '/api/posts/'
        # get no post
        self.login_as_admin()
        rv = self.client.get(api)
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertEqual(data['stat'], 'ok')
        self.assertEqual(data['response']['total_posts'], 0)
        self.assertEqual(data['response']['posts'], [])
        # create posts for test
        import time
        self.client.post('/api/posts/', data={'title': 'python is cool',
                                              'slug': 'python-is-cool',
                                              'text': 'cool, man',
                                              'tags': 'bullet python cool'})
        time.sleep(1)
        self.client.post('/api/posts/', data={'title': 'ruby is bad',
                                              'slug': 'ruby-is-bad',
                                              'text': 'cool, man',
                                              'tags': 'ruby bad'})
        time.sleep(1)
        self.client.post('/api/posts/', data={'title': 'lisp is awesome',
                                              'slug': 'lisp-is-awesome',
                                              'text': 'awesome, man',
                                              'tags': 'lisp cool'})
        time.sleep(1)
        self.client.post('/api/posts/',
                         data={'title': 'secret silver bullet',
                               'slug': 'secrest-silver-bullet',
                               'text': 'you can not touch this',
                               'private': True,
                               'tags': 'bullet cool'})
        time.sleep(1)
        rv = self.client.post('/api/posts/',
                              data={'title': 'garbage language',
                                    'slug': 'garbage-language',
                                    'text': 'you can not touch this',
                                    'tags': 'garbage bad'})
        data = json.loads(rv.data)  # get its id
        # hide it
        self.client.post('/api/posts/trash',
                         data={'id': data['response']['posts'][0]['id']})
        # get all public and private posts
        rv = self.client.get(api)
        data = json.loads(rv.data)
        self.assertEqual(data['stat'], 'ok')
        self.assertEqual(data['response']['total_posts'], 3 + 1)  # 3 public posts and 1 private post
        self.assertEqual(data['response']['posts'][3]['slug'], 'python-is-cool')
        self.assertEqual(data['response']['posts'][2]['slug'], 'ruby-is-bad')
        self.assertEqual(data['response']['posts'][1]['slug'], 'lisp-is-awesome')
        self.assertEqual(data['response']['posts'][0]['slug'], 'secrest-silver-bullet')
        # get date reversed
        rv = self.client.get(api + '?asc')
        data = json.loads(rv.data)
        self.assertEqual(data['response']['posts'][0]['slug'], 'python-is-cool')
        self.assertEqual(data['response']['posts'][1]['slug'], 'ruby-is-bad')
        self.assertEqual(data['response']['posts'][2]['slug'], 'lisp-is-awesome')
        # get only 2 posts
        rv = self.client.get(api + '?limit=2')
        data = json.loads(rv.data)
        self.assertEqual(data['response']['total_posts'], 2)
        # get private posts
        rv = self.client.get(api + '?status=private')
        data = json.loads(rv.data)
        self.assertEqual(data['response']['total_posts'], 1)
        # get trashed posts
        rv = self.client.get(api + '?status=trash')
        data = json.loads(rv.data)
        self.assertEqual(data['response']['total_posts'], 1)
        # invalid status
        rv = self.client.get(api + '?status=invalid')
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.data)
        self.assertEqual(data['stat'], 'fail')
        # get posts by tags
        rv = self.client.get(api + '?tags=python%2Bcool')
        data = json.loads(rv.data)
        self.assertEqual(data['response']['total_posts'], 1)
        self.assertEqual(data['response']['posts'][0]['slug'], 'python-is-cool')
        rv = self.client.get(api + '?tags=cool')
        data = json.loads(rv.data)
        self.assertEqual(data['response']['total_posts'], 2 + 1)  # 2 public posts and 1 private post
        self.assertEqual(data['response']['posts'][0]['slug'], 'secrest-silver-bullet')
        self.assertEqual(data['response']['posts'][1]['slug'], 'lisp-is-awesome')
        # get specified post
        rv = self.client.get(api+'?id=1')
        data = json.loads(rv.data)
        self.assertEqual(data['response']['total_posts'], 1)
        self.assertEqual(data['response']['posts'][0]['title'], 'python is cool')
        # fail: limit is non-number
        rv = self.client.get(api + '?limit=invalid')
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.data)
        self.assertEqual(data['stat'], 'fail')
        self.assertEqual(data['message'], 'invalid limit')
        # fail: offset is non-number
        rv = self.client.get(api + '?offset=invalid')
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.data)
        self.assertEqual(data['stat'], 'fail')
        self.assertEqual(data['message'], 'invalid offset')
