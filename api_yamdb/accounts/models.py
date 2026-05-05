from django.db import models
from django.contrib.auth.models import (
    AbstractUser
)

from .constants import (
    roles,
    CONFIRMATION_CODE_LENGTH,
)

ROLES = tuple(
    (role.name, role.value) for role in roles
)


class Account(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        unique=True,
        verbose_name='Почта'
    )
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_LENGTH,
        blank=True,
        verbose_name='Код подтверждения'
    )
    confirmation_code_expiration_dttm = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Код подтверждения активен до:'
    )
    role = models.CharField(
        default=roles.user.value,
        choices=ROLES,
        max_length=16,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )

    # Неиспользуемые поля родительской модели
    password = None  # ...

    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = (
            '-date_joined',
        )
        verbose_name = 'аккаунт'
        verbose_name_plural = 'Аккаунты'

    def __str__(self):
        return self.username
