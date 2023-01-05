from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import (
    RegisterAccountView
)


router = DefaultRouter()


urlpatterns = [
    path('register', RegisterAccountView.as_view(), name='user-register'),
] + router.urls