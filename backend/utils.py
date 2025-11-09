import string
import random
import hashlib


class ShortCodeGenerator:
    CHARSET = string.ascii_letters + string.digits
    CHARSET = CHARSET.replace('0', '').replace('O', '').replace('l', '').replace('I', '')

    @staticmethod
    def base62_encode(num):
        if num == 0:
            return ShortCodeGenerator.CHARSET[0]

        base = len(ShortCodeGenerator.CHARSET)
        result = []

        while num > 0:
            remainder = num % base
            result.append(ShortCodeGenerator.CHARSET[remainder])
            num //= base

        return ''.join(reversed(result))

    @staticmethod
    def base62_decode(code):
        base = len(ShortCodeGenerator.CHARSET)
        result = 0

        for char in code:
            result = result * base + ShortCodeGenerator.CHARSET.index(char)

        return result

    @staticmethod
    def generate_from_id(url_id, min_length=6):
        code = ShortCodeGenerator.base62_encode(url_id)

        while len(code) < min_length:
            code = ShortCodeGenerator.CHARSET[0] + code

        return code

    @staticmethod
    def generate_from_hash(url, length=7):
        hash_digest = hashlib.sha256(url.encode('utf-8')).hexdigest()

        hash_int = int(hash_digest, 16)

        code = ShortCodeGenerator.base62_encode(hash_int)

        return code[:length]

    @staticmethod
    def generate_random(length=7, avoid_codes=None):
        avoid_codes = avoid_codes or set()
        max_attempts = 1000

        for _ in range(max_attempts):
            code = ''.join(
                random.choices(ShortCodeGenerator.CHARSET, k=length)
            )

            if code not in avoid_codes:
                return code

        return ShortCodeGenerator.generate_random(length + 1, avoid_codes)


class URLValidator:
    VALID_TLDS = {
        'com', 'org', 'net', 'edu', 'gov', 'mil',
        'ir', 'uk', 'de', 'fr', 'jp', 'cn', 'in',
        'io', 'co', 'me', 'dev', 'app', 'ai'
    }

    @staticmethod
    def is_safe_url(url):
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)

            if parsed.scheme not in ['http', 'https']:
                return False, "Protocol should be http or https"

            hostname = parsed.hostname
            if not hostname:
                return False, "Invalid URL"

            return True, "URL is Valid"

        except Exception as e:
            return False, f"Error in checking URL: {str(e)}"
    @staticmethod
    def normalize_and_validate(url):
        url = url.strip()

        if not url:
            return None, "URL couldn't be empty"

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        if len(url) > 2048:
            return None, "URL length is large"

        is_safe, message = URLValidator.is_safe_url(url)
        if not is_safe:
            return None, message

        return url, None
