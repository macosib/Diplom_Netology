from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from users.models import User
from users.serializers import (
    UserSerializer, UserRegisterSerializer
)


class RegisterAccountView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """
        Сохраняем нового пользователя и отправляем email
        с подтверждением регистрации.
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response = {
                'message': "Congratulations on your successful registration. Please confirm your email."
            }
            # data.update(serializer.validated_data)
            return Response(response,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

#
# class RegisterAccount(APIView):
#     """
#     Для регистрации покупателей
#     """
#     # Регистрация методом POST
#     def post(self, request, *args, **kwargs):
#
#         # проверяем обязательные аргументы
#         if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
#             errors = {}
#
#             # проверяем пароль на сложность
#
#             try:
#                 validate_password(request.data['password'])
#             except Exception as password_error:
#                 error_array = []
#                 # noinspection PyTypeChecker
#                 for item in password_error:
#                     error_array.append(item)
#                 return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
#             else:
#                 # проверяем данные для уникальности имени пользователя
#                 request.data._mutable = True
#                 request.data.update({})
#                 user_serializer = UserSerializer(data=request.data)
#                 if user_serializer.is_valid():
#                     # сохраняем пользователя
#                     user = user_serializer.save()
#                     user.set_password(request.data['password'])
#                     user.save()
#                     new_user_registered.send(sender=self.__class__, user_id=user.id)
#                     return JsonResponse({'Status': True})
#                 else:
#                     return JsonResponse({'Status': False, 'Errors': user_serializer.errors})
#
#         return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})