import json
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class URLCache:
    PREFIX_SHORT_CODE = 'url:short:'
    PREFIX_HASH = 'url:hash:'
    PREFIX_EXISTS = 'url:exists:'

    CACHE_TTL = 86400
    CACHE_TTL_LONG = 604800

    @staticmethod
    def _make_key(prefix, value):
        return f"{prefix}{value}"

    @staticmethod
    def get_by_short_code(short_code):
        key = URLCache._make_key(URLCache.PREFIX_SHORT_CODE, short_code)

        try:
            cached_data = cache.get(key)
            if cached_data:
                logger.debug(f"Cache HIT for short_code: {short_code}")
                return json.loads(cached_data) if isinstance(cached_data, str) else cached_data

            logger.debug(f"Cache MISS for short_code: {short_code}")
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    @staticmethod
    def set_by_short_code(short_code, url_data, ttl=None):
        key = URLCache._make_key(URLCache.PREFIX_SHORT_CODE, short_code)
        ttl = ttl or URLCache.CACHE_TTL_LONG

        try:
            cache.set(key, json.dumps(url_data), ttl)
            logger.debug(f"Cached short_code: {short_code}")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    @staticmethod
    def get_by_hash(url_hash):
        key = URLCache._make_key(URLCache.PREFIX_HASH, url_hash)

        try:
            cached_data = cache.get(key)
            if cached_data:
                logger.debug(f"Cache HIT for hash: {url_hash[:16]}...")
                return json.loads(cached_data) if isinstance(cached_data, str) else cached_data

            logger.debug(f"Cache MISS for hash: {url_hash[:16]}...")
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    @staticmethod
    def set_by_hash(url_hash, url_data, ttl=None):
        key = URLCache._make_key(URLCache.PREFIX_HASH, url_hash)
        ttl = ttl or URLCache.CACHE_TTL

        try:
            cache.set(key, json.dumps(url_data), ttl)
            logger.debug(f"Cached hash: {url_hash[:16]}...")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    @staticmethod
    def invalidate_short_code(short_code):
        key = URLCache._make_key(URLCache.PREFIX_SHORT_CODE, short_code)

        try:
            cache.delete(key)
            logger.debug(f"Invalidated cache for short_code: {short_code}")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False

    @staticmethod
    def invalidate_hash(url_hash):
        key = URLCache._make_key(URLCache.PREFIX_HASH, url_hash)

        try:
            cache.delete(key)
            logger.debug(f"Invalidated cache for hash: {url_hash[:16]}...")
            return True
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False

    @staticmethod
    def check_short_code_exists(short_code):
        key = URLCache._make_key(URLCache.PREFIX_EXISTS, short_code)

        try:
            exists = cache.get(key)
            if exists is not None:
                return bool(exists)

            return None

        except Exception as e:
            logger.error(f"Error checking existence in cache: {e}")
            return None

    @staticmethod
    def mark_short_code_exists(short_code, exists=True, ttl=None):
        key = URLCache._make_key(URLCache.PREFIX_EXISTS, short_code)
        ttl = ttl or URLCache.CACHE_TTL_LONG

        try:
            cache.set(key, 1 if exists else 0, ttl)
            return True
        except Exception as e:
            logger.error(f"Error marking existence in cache: {e}")
            return False

    @staticmethod
    def warm_cache(url_obj):
        url_data = {
            'original_url': url_obj.original_url,
            'short_code': url_obj.short_code,
            'url_hash': url_obj.url_hash,
        }

        URLCache.set_by_short_code(url_obj.short_code, url_data)

        URLCache.set_by_hash(url_obj.url_hash, url_data)

        URLCache.mark_short_code_exists(url_obj.short_code, exists=True)

        logger.info(f"Warmed cache for: {url_obj.short_code}")

    @staticmethod
    def clear_all_for_url(url_obj):
        URLCache.invalidate_short_code(url_obj.short_code)
        URLCache.invalidate_hash(url_obj.url_hash)

        logger.info(f"Cleared all cache for: {url_obj.short_code}")