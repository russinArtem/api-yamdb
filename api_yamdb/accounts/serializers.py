from rest_framework import serializers
from django.contrib.auth import get_user_model

FORBIDDEN_UESRNAMES = (
    'me',
)

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        if value in FORBIDDEN_UESRNAMES:
            raise serializers.ValidationError(
                f'Имя {value} запрещено'
            )
        return value

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False}
        }


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Неверный код подтверждения.")

        return data
