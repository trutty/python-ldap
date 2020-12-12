import time
import unittest

from ldapauth.main.cache import Cache


class TestCache(unittest.TestCase):

    def test_cache(self):
        cache_key_expiration_seconds = 2
        cache = Cache(cache_key_expiration_seconds)
        # entry not yet cached
        ret = cache.validate('user0', 'my-config', 'test123')
        self.assertFalse(ret)
        # add entry
        cache.set('user0', 'my-config', 'test123')

        # check with wrong password
        ret = cache.validate('user0', 'my-config', 'wrong-pw')
        self.assertFalse(ret)
        # check with correct password
        ret = cache.validate('user0', 'my-config', 'test123')
        self.assertTrue(ret)

        # wait until cache expired and check again
        time.sleep(cache_key_expiration_seconds)
        ret = cache.validate('user0', 'my-config', 'test123')
        self.assertFalse(ret)


if __name__ == '__main__':
    unittest.main()
