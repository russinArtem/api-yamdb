from rest_framework import serializers, exceptions
from django.contrib.auth.validators import (
    UnicodeUsernameValidator
)
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from accounts.constants import (
    CONFIRMATION_CODE_LENGTH,
    EMAIL_LENGTH,
    USERNAME_LENGTH,
)

FORBIDDEN_UESRNAMES = (
    'me',
)

User = get_user_model()


class SignupSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True,
        validators=(
            UnicodeUsernameValidator(),
        ),
    )
    email = serializers.EmailField(
        max_length=EMAIL_LENGTH,
        required=True,
    )

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        user_by_username = User.objects.filter(
            username=username
        ).first()

        if user_by_username and (user_by_username.email != email):
            raise serializers.ValidationError(
                'Пользователь с таким Email уже существует.'
            )

        user_by_email = User.objects.filter(
            email=email
        ).first()

        if user_by_email and (user_by_email.username != username):
            raise serializers.ValidationError(
                'Нельзя регистрировать разных пользователей на один Email.'
            )

        return attrs

    def validate_username(self, username):
        if username in FORBIDDEN_UESRNAMES:
            raise serializers.ValidationError(
                f'Имя {username} запрещено'
            )
        return username

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            username=validated_data.get('username'),
            email=validated_data.get('email')
        )
        return user


class TokenObtainSerializer(serializers.Serializer):

    username = serializers.CharField()
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LENGTH
    )

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as not_exist:
            raise exceptions.NotFound(
                'Пользователь не найден.'
            ) from not_exist

        if not default_token_generator.check_token(
            user=user,
            token=confirmation_code
        ):
            raise serializers.ValidationError('Неверный код подтверждения.')

        return data
