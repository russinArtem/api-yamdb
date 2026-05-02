import random

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import (
    get_object_or_404,
)
from django.utils import timezone


from .models import (
    CODE_EXPIRATION_LIMIT,
)
from .serializers import (
    SignupSerializer,
    TokenObtainSerializer
)

User = get_user_model()


class SignUpViewSet(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        confirmation_code, expiration_dttm = self._confirmation_code()

        try:
            username = request.data.get('username')
            email = request.data.get('email')
        except KeyError:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(
                username=username,
                email=email
            )
            user.confirmation_code = confirmation_code
            user.confirmation_code_expiration_dttm = expiration_dttm
            user.save(
                update_fields=(
                    'confirmation_code',
                    'confirmation_code_expiration_dttm'
                )
            )

        except User.DoesNotExist:
            # Если юзера нет, создаём его
            serializer.is_valid(raise_exception=True)
            serializer.save(
                confirmation_code=confirmation_code,
                confirmation_code_expiration_dttm=expiration_dttm
            )
        self._send_code(
            recipient=email,
            confirmation_code=confirmation_code
        )
        return Response(
            data={
                'email': email,
                'username': username,
            },
            status=status.HTTP_200_OK
        )

    def _confirmation_code(self):
        confirmation_code = f'{str(random.randint(0, 999999)):{'0'}>6}'
        confirmation_code_expiration_dttm = (
            timezone.now() + CODE_EXPIRATION_LIMIT
        )
        return confirmation_code, confirmation_code_expiration_dttm

    def _send_code(self, recipient, confirmation_code):
        send_mail(
            subject='Код подтверждения',
            message=f'''
                Ваш код подтверждения: {confirmation_code}.
                Если вы не отправляли запрос, ничего не делайте.
            '''.replace('    ', ''),
            from_email='SgtPepeF@yandex.ru',
            recipient_list=[recipient],
            fail_silently=False,
        )


class TokenObtainViewSet(APIView):

    permission_classes = (permissions.AllowAny,)

    def _get_user(self):
        username = self.request.data.get('username')
        return get_object_or_404(
            User,
            username=username
        )

    def post(self, request):
        if any(
            f not in request.data for f in ('username', 'confirmation_code',)
        ):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenObtainSerializer(data=request.data)
        user = self._get_user()

        if serializer.is_valid():

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
