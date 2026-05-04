"""Файл констант приложения accounts."""

from datetime import timedelta
from enum import Enum


class roles(Enum):
    user = 'user'
    moderator = 'moderator'
    admin = 'admin'


CONFIRMATION_CODE_LENGTH = 64
CODE_EXPIRATION_LIMIT = timedelta(hours=1)
