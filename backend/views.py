from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.db import transaction, IntegrityError
import hashlib
import logging


from models import URL
from utils import ShortCodeGenerator, URLValidator
from cache import URLCache

logger = logging.getLogger(__name__)


class ShortenURLView(APIView):
    def post(self, request):
        try:
            original_url = request.data.get('url', '').strip()

            if not original_url:
                return Response(
                    {'error': 'URL Can not be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            normalized_url, error = URLValidator.normalize_and_validate(original_url)

            if error:
                return Response(
                    {'error': error},
                    status=status.HTTP_400_BAD_REQUEST
                )

            url_hash = hashlib.sha256(normalized_url.encode('utf-8')).hexdigest()

            cached_url = URLCache.get_by_hash(url_hash)
            if cached_url:
                logger.info(f"URL found in cache: {cached_url['short_code']}")
                return self._build_response(request, cached_url['short_code'])

            try:
                existing_url = URL.objects.get(url_hash=url_hash)
                logger.info(f"URL found in database: {existing_url.short_code}")

                URLCache.warm_cache(existing_url)

                return self._build_response(request, existing_url.short_code)

            except URL.DoesNotExist:
                pass

            url_obj = self._create_url_with_collision_handling(
                normalized_url,
                url_hash
            )

            if not url_obj:
                return Response(
                    {'error': 'ERR in creating short URL'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            URLCache.warm_cache(url_obj)

            logger.info(f"Created new short URL: {url_obj.short_code}")

            return self._build_response(request, url_obj.short_code)

        except Exception as e:
            logger.error(f"Error in ShortenURLView: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Internal server error. please retry.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _create_url_with_collision_handling(self, url, url_hash, max_attempts=10):
        for attempt in range(max_attempts):
            try:
                short_code = ShortCodeGenerator.generate_from_hash(url, length=7 + attempt)
                exists_in_cache = URLCache.check_short_code_exists(short_code)
                if exists_in_cache:
                    logger.warning(f"Short code {short_code} exists in cache, retrying...")
                    continue

                with transaction.atomic():
                    url_obj = URL.objects.create(
                        original_url=url,
                        short_code=short_code,
                        url_hash=url_hash
                    )

                    URLCache.mark_short_code_exists(short_code, exists=True)

                    return url_obj

            except IntegrityError as e:
                logger.warning(f"Collision detected for short_code: {short_code}, attempt {attempt + 1}")

                if 'url_hash' in str(e):
                    try:
                        return URL.objects.get(url_hash=url_hash)
                    except URL.DoesNotExist:
                        pass

                continue

            except Exception as e:
                logger.error(f"Unexpected error creating URL: {str(e)}")
                break

        logger.error(f"Failed to create short code after {max_attempts} attempts")
        return None

    def _build_response(self, request, short_code):
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        short_url = f"{protocol}://{host}/{short_code}"

        return Response(
            {
                'short_code': short_code,
                'short_url': short_url
            },
            status=status.HTTP_201_CREATED
        )


class RedirectView(APIView):
    def get(self, request, short_code):
        try:
            if not short_code or len(short_code) > 20:
                raise Http404("Invalid code")

            cached_url = URLCache.get_by_short_code(short_code)
            if cached_url:
                logger.info(f"Redirecting from cache: {short_code}")
                return redirect(cached_url['original_url'], permanent=False)

            try:
                url_obj = URL.objects.get(short_code=short_code)

                URLCache.warm_cache(url_obj)

                logger.info(f"Redirecting from database: {short_code}")

                return redirect(url_obj.original_url, permanent=False)

            except URL.DoesNotExist:
                logger.warning(f"Short code not found: {short_code}")
                raise Http404("Couldn't find URL")

        except Http404:
            raise
        except Exception as e:
            logger.error(f"Error in RedirectView: {str(e)}", exc_info=True)
            return JsonResponse(
                {'error': 'Server error'},
                status=500
            )
