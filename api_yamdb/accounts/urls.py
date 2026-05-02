from django.urls import path
from rest_framework import routers

from .views import (
    SignUpViewSet,
    TokenObtainViewSet,
)

router_auth_v1 = routers.DefaultRouter()

urlpatterns = [
    path('signup/', SignUpViewSet.as_view()),
    path('token/', TokenObtainViewSet.as_view())
]
