from django.db import models
from django.contrib.auth.models import (
    AbstractUser
)

ROLES = (
    ('U', 'user'),
    ('M', 'moderator'),
    ('A', 'admin'),
)


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(unique=True)

    role = models.CharField(default='U', choices=ROLES, max_length=16)
    bio = models.TextField(blank=True, null=True)

    # Неиспользуемые поля родительской модели
    password = None  # ...
    is_superuser = None
    is_staff = None
    last_login = None
    is_active = None
    date_joined = None
