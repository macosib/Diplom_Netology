from django.contrib.auth.backends import UserModel
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers

from users.models import User, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }

class AccountRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'password', 'password_confirm')
        read_only_fields = ('id',)

    def validate(self, data):
        """
        Validation of password confirmation
        """
        password = data['password']
        password_confirm = data.pop('password_confirm')
        try:
            if password != password_confirm:
                raise ValueError("You need to confirm the password. Passwords don't match")
            validate_password(password)
        except Exception as error:
            raise serializers.ValidationError(
                {'password': error}
            )
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class AccountLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        password = data['password']
        email = data['email']
        user = authenticate(username=email, password=password)
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                {"status": "Failure", "error": "Failed to authorize"}
            )
        return user




class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts')
        read_only_fields = ('id',)
