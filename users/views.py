from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, ConfirmEmailToken
from users.serializers import (
    AccountRegisterSerializer,
)
from users.signals import new_user_registered


class RegisterAccountView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AccountRegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        Регистрируем нового пользователя и отпрляем письмо с токеном для завершения регистрации.
        """
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
    def post(self, request):
        """
        Класс для подтверждения регистрации пользователя.
        """
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     token=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return JsonResponse({
                    "status": "Success",
                    'message': "Account confirmed"
                }, status=status.HTTP_200_OK)

        return JsonResponse({"status": "Failure", "error": "It is necessary to provide an email and a token"},
                            status=status.HTTP_400_BAD_REQUEST)
