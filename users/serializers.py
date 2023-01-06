from django.contrib.auth.password_validation import validate_password
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
        fields = ('id', 'email', 'company', 'position', 'password', 'password_confirm')
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

class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts')
        read_only_fields = ('id',)
