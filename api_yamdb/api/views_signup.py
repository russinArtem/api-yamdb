from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from .serializers_signup import (
    SignupSerializer,
    TokenObtainSerializer
)

User = get_user_model()


class SignUpViewSet(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        confirmation_code = default_token_generator.make_token(user)

        self._send_code(
            recipient=user.email,
            confirmation_code=confirmation_code
        )
        return Response(
            data={
                'email': user.email,
                'username': user.username,
            },
            status=status.HTTP_200_OK
        )

    def _send_code(self, recipient, confirmation_code):
        send_mail(
            subject='Код подтверждения',
            message=f'''
                Ваш код подтверждения: {confirmation_code}
                Если вы не отправляли запрос, ничего не делайте.
            '''.replace('    ', ''),
            from_email=None,
            recipient_list=(recipient,),
            fail_silently=False,
        )


class TokenObtainViewSet(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(
            username=serializer.validated_data['username']
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_200_OK
        )
