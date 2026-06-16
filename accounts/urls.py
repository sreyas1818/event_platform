from django.urls import path
from .views import (
    SignupView,
    VerifyEmailView,
    LoginView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path(
        'signup',
        SignupView.as_view(),
        name='signup'
    ),

    path(
        'verify-email',
        VerifyEmailView.as_view(),
        name='verify-email'
    ),
    path(
        'login',
        LoginView.as_view()
    ),
    path(
        'refresh',
        TokenRefreshView.as_view(),
        name='token_refresh'
),
]