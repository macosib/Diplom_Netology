from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import (
    RegisterAccountView, ConfirmAccountView, LoginAccountView
)

router = DefaultRouter()

urlpatterns = [
    path('register/confirm', ConfirmAccountView.as_view(), name='user-register-confirm'),
    path('register', RegisterAccountView.as_view(), name='user-register'),
    path('login', LoginAccountView.as_view(), name='user-login'),
] + router.urls