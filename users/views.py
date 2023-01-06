from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import (
    AccountRegisterSerializer, AccountLoginSerializer, AccountConfirmSerializer, )
from users.signals import new_user_registered


class RegisterAccountView(CreateAPIView):
    """
    Регистрируем нового пользователя и отпрляем письмо с токеном для завершения регистрации.
    """
    queryset = User.objects.all()
    serializer_class = AccountRegisterSerializer

    def post(self, request, *args, **kwargs):

        serializer = AccountRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            new_user_registered.send(sender=self.__class__, user=user)
            response = {
                "status": "Success",
                'message': "Congratulations on your successful registration. Please confirm your email"
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmAccountView(APIView):
    """
    Класс для подтверждения регистрации пользователя.
    """
    serializer_class = AccountConfirmSerializer

    def post(self, request):
        serializer = AccountConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data
            token.user.save()
            token.delete()
            return JsonResponse({
                "status": "Success",
                'message': "Account confirmed"
            }, status=status.HTTP_200_OK)

        return JsonResponse({"status": "Failure", "error": "It is necessary to provide an email and a token"},
                            status=status.HTTP_400_BAD_REQUEST)


class LoginAccountView(APIView):
    """
    Аутентификация пользователя и получение токена
    """
    serializer_class = AccountLoginSerializer

    def post(self, request):
        serializer = AccountLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'status': 'Success', 'token': token.key}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
