from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import (
    AbstractUser
)

CODE_EXPIRATION_LIMIT = timedelta(hours=1)
CONFIRMATION_CODE_LENGTH = 6

ROLES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(unique=True)

    confirmation_code = models.CharField(max_length=6, blank=True)
    confirmation_code_expiration_dttm = models.DateTimeField(
        default=(datetime.now() + CODE_EXPIRATION_LIMIT)
    )

    role = models.CharField(default='user', choices=ROLES, max_length=16)
    bio = models.TextField(blank=True, null=True)

    # Неиспользуемые поля родительской модели
    password = None  # ...

    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = (
            '-date_joined',
        )
