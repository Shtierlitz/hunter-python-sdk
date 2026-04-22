"""Shared constants for the Hunter SDK."""

from datetime import timedelta

BASE_URL = "https://api.hunter.io/v2"
DEFAULT_TIMEOUT = timedelta(seconds=10).total_seconds()
DEFAULT_DOMAIN_SEARCH_LIMIT = 10
HTTP_STATUS_OK = 200
HTTP_STATUS_ACCEPTED = 202

FIELD_DOMAIN = "domain"
FIELD_EMAIL = "email"
FIELD_STATUS = "status"
FIELD_RESULT = "result"
FIELD_SCORE = "score"
FIELD_ORGANIZATION = "organization"
FIELD_PATTERN = "pattern"
FIELD_EMAILS = "emails"
FIELD_FIRST_NAME = "first_name"
FIELD_LAST_NAME = "last_name"
