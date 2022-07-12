from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from apps.users.views import UserCreateAPIView

urlpatterns = [
    path('register/', UserCreateAPIView.as_view()),
    path('api-token-auth/', TokenObtainPairView.as_view()),
    path('api-token-refresh/', TokenRefreshView.as_view()),
]
