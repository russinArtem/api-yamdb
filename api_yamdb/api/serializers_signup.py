from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from accounts.constants import (
    CONFIRMATION_CODE_LENGTH,
)

FORBIDDEN_UESRNAMES = (
    'me',
)

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

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
            raise serializers.ValidationError(
                'Пользователь не найден.'
            ) from not_exist

        if not default_token_generator.check_token(
            user=user,
            token=confirmation_code
        ):
            raise serializers.ValidationError('Неверный код подтверждения.')

        return data
