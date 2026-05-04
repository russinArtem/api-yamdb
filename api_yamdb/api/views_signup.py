from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.mixins import (
    CreateModelMixin,
)

from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import (
    get_object_or_404,
)

from .serializers_signup import (
    SignupSerializer,
    TokenObtainSerializer
)

User = get_user_model()


# class SignUpViewSet(
#     viewsets.GenericViewSet,
#     CreateModelMixin
# ):
#     permission_classes = (permissions.AllowAny,)
#     queryset = User.objects.all()
#     serializer_class = SignupSerializer

class SignUpViewSet(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        serializer = SignupSerializer(data=request.data)

        user = self._get_user()
        serializer.is_valid(raise_exception=True)

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
    
    def _get_user(self):
        username = self.request.data.get('username')
        return get_object_or_404(
            User,
            username=username
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

    def _get_user(self):
        username = self.request.data.get('username')
        return get_object_or_404(
            User,
            username=username
        )

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        user = self._get_user()
        serializer.is_valid(raise_exception=True)

        refresh = RefreshToken.for_user(user)

        return Response(
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_200_OK
        )
