from time import time
from werkzeug.contrib.cache import BaseCache as _Cache
try:
    import cPickle as pickle
except ImportError:
    import pickle


class CacheError(Exception):
    pass


class Cache(_Cache):
    def __init__(self, threshold=None, default_timeout=300):
        _Cache.__init__(self, default_timeout)
        self._threshold = threshold
        self._cache = {}        # key: (time, value)
        self._hits = []         # (key, hits)
        self._pos = {}          # key: pos

    def _prune(self):
        if self._threshold is not None \
                and len(self._hits) > self._threshold:
            for i in xrange(max(1, len(self._hits)//8)):
                key, _ = self._hits.pop()
                self._cache.pop(key, None)

    def get_hits(self, key):
        pos = self.get_pos(key)
        if pos is not None:
            return self._hits[pos][1]

    def get_pos(self, key):
        return self._pos.get(key)

    def keys(self):
        return self._cache.keys()

    def values(self):
        return self._cache.values()

    def items(self):
        return self._cache.items()

    def get(self, key, hit=True):
        if hit:
            self.inc_hits(key)
        now = time()
        expires, value = self._cache.get(key, (0, None))
        if expires > time():
            return pickle.loads(value)

    def delete(self, key):
        if key in self._cache:
            assert(key in self._pos)
            pos = self.get_pos(key)
            assert(pos is not None)
            self._hits.pop(pos)
            for k, _ in self._hits[pos:]:
                self._pos[k] -= 1
            self._pos.pop(key)
            self._cache.pop(key)

    def clear(self):
        self._cache.clear()
        self._hits = []
        self._pos.clear()

    def inc_hits(self, key):
        if key in self._pos:
            pq = self._hits
            pos = self.get_pos(key)
            hits = self.get_hits(key) + 1
            pq[pos] = key, hits
            while pos-1 >= 0 and hits > pq[pos-1][1]:
                pos -= 1
                self._swap(pos, pos+1)
            return hits

    def dec_hits(self, key):
        if key in self._pos:
            pq = self._hits
            pos = self.get_pos(key)
            hits = max(0, self.get_hits(key)-1)
            pq[pos] = key, hits
            while pos+1 < len(pq) and hits < pq[pos+1][1]:
                pos += 1
                self._swap(pos, pos-1)
            return hits

    def get_sorted_hits(self, reverse=False):
        """ sort by hits """
        return sorted(self._hits, lambda a, b: a[1]-b[1])


    def _swap(self, pos, other):
        pq = self._hits
        pq[pos], pq[other] = \
            pq[other], pq[pos]
        self._pos[pq[pos][0]] = pos
        self._pos[pq[other][0]] = other

    def reset_hits(self, key):
        # todo: swap is better
        if key in self._pos:
            # remove hits of key
            pos = self.get_pos(key)
            assert(pos is not None)
            self._hits.pop(pos)
            self._pos.pop(key)
            for k, _ in self._hits[pos:]:
                self._pos[k] -= 1
            # append again
            self._hits.append((key, 0)) # key and hits
            self._pos[key] = len(self._hits) - 1 # pos

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        self._prune()
        if key in self._pos:
            self.reset_hits(key)
        else:
            self._hits.append((key, 0)) # hits
            self._pos[key] = len(self._hits) - 1 # pos
        self._cache[key] = (time() + timeout,
                            pickle.dumps(value, pickle.HIGHEST_PROTOCOL))

    def add(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        self._prune()
        item = (time() + timeout,
                pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
        self._cache.setdefault(key, item)

    def cache(self, fetcher):
        """ Cache the value returned by fetcher which takes a key as its argument. """
        def _fetcher(key, *args, **kwargs):
            result = self.get(key)
            if result is None:
                result = fetcher(key, *args, **kwargs)
                if result is not None:
                    self.set(key, result)
            return result
        return _fetcher

    def cache_many(self, fetcher):
        def _cache_many(key_list, *args, **kwargs):
            results = self.get_many(*key_list)
            misses = []
            for key, result in zip(key_list, results):
                if result is None:
                    misses.append(key)
            final = []
            if len(misses):
                fresh = fetcher(misses, *args, **kwargs)
                if len(fresh) != len(misses):
                    raise CacheError('return not as many as input')
                self.set_many(dict(zip(misses, fresh)))
                fresh.reverse()
                for result in results:
                    if result is None:
                        final.append(fresh.pop())
                    else:
                        final.append(result)
            else:
                final = results
            if len(final) != len(key_list):
                raise CacheError('return not as many as input')
            return final
        return _cache_many

    def cache_to(self, key):
        """ cache the value return by the fetcher to the key. """
        def _helper(fetcher):
            def _real_cache(*args, **kwargs):
                result = self.get(key)
                if result is None:
                    result = fetcher(*args, **kwargs)
                    if result is not None:
                        self.set(key, result)
                return result
            return _real_cache
        return _helper

    # def delete_cache(self, deleter):
    #     def _delete(key, *args, **kwargs):
    #         deleter(key, *args, **kwargs)
    #         self.delete(key)
    #     return _also_delete
