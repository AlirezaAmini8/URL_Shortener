from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import hashlib


class URL(models.Model):
    original_url = models.TextField(
        validators=[URLValidator()],
        db_index=True
    )
    short_code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    url_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True
    )

    class Meta:
        app_label = 'backend'
        db_table = 'urls'
        managed = True

    def save(self, *args, **kwargs):
        if not self.url_hash:
            self.url_hash = hashlib.sha256(
                self.original_url.encode('utf-8')
            ).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}"

    @staticmethod
    def normalize_url(url):
        url = url.strip()

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        if '?' not in url and url.endswith('/'):
            url = url.rstrip('/')

        return url

    @staticmethod
    def validate_url(url):
        validator = URLValidator(
            schemes=['http', 'https']
        )

        try:
            validator(url)
        except ValidationError:
            raise ValidationError("Invalid URL")

        if len(url) > 2048:
            raise ValidationError("URL Length is large. please provide another URL.")

        dangerous_patterns = ['javascript:', 'data:', 'vbscript:']
        url_lower = url.lower()
        for pattern in dangerous_patterns:
            if pattern in url_lower:
                raise ValidationError("This URL has dangerous patterns.")

        return True