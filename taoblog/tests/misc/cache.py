import unittest
from taoblog.cache import Cache


class TestCache(unittest.TestCase):
    def test_set(self):
        a = Cache()
        a.set(1, 'hello')
        a.set(2, 'world')
        self.assertEqual(a.get_hits(1), 0)
        self.assertEqual(a.get_pos(1), 0)
        self.assertEqual(a.get_hits(2), 0)
        self.assertEqual(a.get_pos(2), 1)
        a.get(2)
        self.assertEqual(a.get_hits(1), 0)
        self.assertEqual(a.get_pos(1), 1)
        self.assertEqual(a.get_hits(2), 1)
        self.assertEqual(a.get_pos(2), 0)
        a.get(2, hit=False)
        self.assertEqual(a.get_hits(2), 1)
        self.assertEqual(a.get_pos(2), 0)
        a.set(1, 100)
        self.assertEqual(a.get(1, hit=False), 100)
        self.assertEqual(a.get_hits(1), 0)
        self.assertEqual(a.get_pos(2), 0)
        self.assertEqual(a.get_pos(1), 1)
        a.set(2, 200)
        self.assertEqual(a.get(2, hit=False), 200)
        self.assertEqual(a.get_hits(2), 0)
        self.assertEqual(a.get_pos(2), 1)
        self.assertEqual(a.get_pos(1), 0)

    def test_delete(self):
        a = Cache()
        a.set(1, 100)
        a.get(1)
        a.set(2, 200)
        self.assertEqual(a.get_hits(1), 1)
        self.assertEqual(a.get_pos(1), 0)
        self.assertEqual(a.get_pos(2), 1)
        a.delete(1)
        self.assertEqual(a.get_pos(2), 0)

    def test_hits(self):
        a = Cache()
        self.assertEqual(a.get_hits('none'), None)
        self.assertEqual(a.get_pos('none'), None)
        hit_table = {'to': 20,
                     'have': 30,
                     'cool': 1,
                     'I': 50,
                     'is': 2,
                     'this': 6,
                     'say': 7}
        for key, hits in hit_table.items():
            a.set(key, str(key)+' value')
            for i in xrange(hits):
                a.get(key)
        for key, hits in hit_table.items():
            self.assertEqual(a.get_hits(key), hits)
        self.assertEqual('I have to say this is cool',
                         ' '.join(key for key, hits in a._hits))
        for key in a.keys():
            self.assertEqual(a._hits[a.get_pos(key)][0], key)
        for key, hits in hit_table.items():
            for i in xrange(hits):
                a.dec_hits(key)
            self.assertEqual(a.get_hits(key), 0)

    def test_cache_decorator(self):
        a = Cache()
        counter = {}
        dicta = {
            1: 'this',
            2: 'is',
            3: 'cool',
            4: 'I',
            5: 'miss',
            6: 'you'}
        @a.cache
        def get_key(key):
            counter[key] = counter.setdefault(key, 0) + 1
            # print counter
            return dicta.get(key)

        self.assertEqual(get_key(1), 'this')
        self.assertEqual(counter[1], 1)

        self.assertEqual(a.get(1), 'this')
        self.assertEqual(get_key(1), 'this')
        self.assertEqual(counter[1], 1)

        self.assertEqual(get_key(2), 'is')
        self.assertEqual(counter[2], 1)

        a.delete(2)
        self.assertEqual(a.get(2), None)

        self.assertEqual(get_key(2), 'is')
        self.assertEqual(counter[2], 2)

        # a = Cache()
        a.clear()
        counter = {}
        @a.cache_many
        def get_many_key(key_list):
            for key in key_list:
                counter[key] = counter.setdefault(key, 0) + 1
            return map(dicta.get, key_list)

        many = get_many_key([1, 2, 3])
        self.assertEqual(many, ['this', 'is', 'cool'])
        self.assertEqual(a.get(1), 'this')
        self.assertEqual(a.get(2), 'is')
        self.assertEqual(a.get(3), 'cool')
        self.assertEqual(counter[1], 1)
        self.assertEqual(counter[2], 1)
        self.assertEqual(counter[3], 1)
        self.assertEqual(a.get_hits(1), 1)
        self.assertEqual(a.get_hits(2), 1)
        self.assertEqual(a.get_hits(3), 1)
        many = get_many_key([2, 3, 4])
        self.assertEqual(many, ['is', 'cool', 'I'])
        self.assertEqual(counter[1], 1)
        self.assertEqual(counter[2], 1)
        self.assertEqual(counter[3], 1)
        self.assertEqual(counter[4], 1)
        self.assertEqual(a.get_hits(1), 1)
        self.assertEqual(a.get_hits(2), 2)
        self.assertEqual(a.get_hits(3), 2)
        self.assertEqual(a.get_hits(4), 0)
        many = get_many_key([6, 4, 1, 2, 5])
        self.assertEqual(many, ['you', 'I', 'this', 'is', 'miss'])

    def test_threshold(self):
        a = Cache(20)
        for k in xrange(40):
            a.set(k, k * k)
        self.assertEqual(len(a.keys()), 20)
