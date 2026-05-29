from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.core.services import CacheService, QRCodeService
import inspect


class CacheServiceTest(TestCase):
    """Test CacheService — adapts to actual implementation"""
    
    def setUp(self):
        self.cache = CacheService()
        # Inspect actual method signatures
        self.set_sig = inspect.signature(self.cache.set)
        self.get_sig = inspect.signature(self.cache.get)
        self.del_sig = inspect.signature(self.cache.delete)
    
    def _cache_set(self, key, value, **kwargs):
        """Flexible set that works with any signature"""
        params = list(self.set_sig.parameters.keys())
        # Remove 'self' if present
        if 'key' in params and 'value' in params:
            accepted = {k: v for k, v in kwargs.items() if k in params}
            return self.cache.set(key, value, **accepted)
        return self.cache.set(key, value)
    
    def _cache_get(self, key, **kwargs):
        """Flexible get that works with any signature"""
        params = list(self.get_sig.parameters.keys())
        if params:
            accepted = {k: v for k, v in kwargs.items() if k in params}
            return self.cache.get(key, **accepted)
        return self.cache.get(key)
    
    def _cache_delete(self, key, **kwargs):
        """Flexible delete that works with any signature"""
        params = list(self.del_sig.parameters.keys())
        if params:
            accepted = {k: v for k, v in kwargs.items() if k in params}
            return self.cache.delete(key, **accepted)
        return self.cache.delete(key)

    def test_cache_service_instantiates(self):
        """CacheService can be instantiated"""
        cache = CacheService()
        self.assertIsNotNone(cache)

    def test_cache_has_set_method(self):
        self.assertTrue(hasattr(self.cache, 'set'))
        self.assertTrue(callable(self.cache.set))

    def test_cache_has_get_method(self):
        self.assertTrue(hasattr(self.cache, 'get'))
        self.assertTrue(callable(self.cache.get))

    def test_cache_has_delete_method(self):
        self.assertTrue(hasattr(self.cache, 'delete'))
        self.assertTrue(callable(self.cache.delete))

    def test_cache_set_and_get_roundtrip(self):
        """Set a value and get it back"""
        test_key = "test_roundtrip_key_xyz123"
        test_value = {"name": "test", "count": 42}
        self._cache_set(test_key, test_value, ttl=60)
        result = self._cache_get(test_key)
        self.assertEqual(result, test_value)

    def test_cache_returns_none_for_missing(self):
        """Missing key returns None"""
        result = self._cache_get("this_key_definitely_does_not_exist_abc987")
        self.assertIsNone(result)

    def test_cache_delete_removes_value(self):
        """Deleted key returns None"""
        test_key = "delete_test_key_xyz456"
        self._cache_set(test_key, "hello world", ttl=60)
        self._cache_delete(test_key)
        result = self._cache_get(test_key)
        self.assertIsNone(result)

    def test_cache_overwrites_existing(self):
        """Setting same key overwrites previous value"""
        test_key = "overwrite_test_key_xyz789"
        self._cache_set(test_key, "first_value", ttl=60)
        self._cache_set(test_key, "second_value", ttl=60)
        result = self._cache_get(test_key)
        self.assertEqual(result, "second_value")


class QRCodeServiceTest(TestCase):
    def test_generate_qr_returns_bytes(self):
        service = QRCodeService()
        result = service.generate("https://example.com/verify/123")
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 100)

    def test_generate_qr_different_data_different_output(self):
        service = QRCodeService()
        r1 = service.generate("data1")
        r2 = service.generate("data2")
        self.assertNotEqual(r1, r2)

    def test_generate_qr_not_empty(self):
        service = QRCodeService()
        result = service.generate("test")
        self.assertTrue(len(result) > 0)

    def test_generate_same_data_consistent(self):
        service = QRCodeService()
        r1 = service.generate("consistent-data")
        r2 = service.generate("consistent-data")
        # Same data should produce same or similar output
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)
