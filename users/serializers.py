from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User, Contact, ConfirmEmailToken


class AccountContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "id",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
            "phone",
            "user",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"user": {"write_only": True}}

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().update(instance, validated_data)


class AccountSerializer(serializers.ModelSerializer):
    contacts = AccountContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "company",
            "position",
            "contacts",
        )
        read_only_fields = ("id",)


class AccountRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, required=True)
    type = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "company",
            "position",
            "password",
            "password_confirm",
            "type",
        )
        read_only_fields = ("id",)

    def validate(self, data):
        """
        Validation of password confirmation
        """
        password = data["password"]
        password_confirm = data.pop("password_confirm")
        try:
            if password != password_confirm:
                raise ValueError(
                    "You need to confirm the password. Passwords don't match"
                )
            validate_password(password)
        except Exception as error:
            raise serializers.ValidationError({"status": "Failure", "error": error})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AccountLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        password = data["password"]
        email = data["email"]
        user = authenticate(username=email, password=password)
        if user is None or not user.is_active:
            raise serializers.ValidationError(
                {"status": "Failure", "error": "Failed to authorize"}
            )
        return user


class AccountConfirmSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    token = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        email = data["email"]
        token_request = data["token"]

        token = ConfirmEmailToken.objects.filter(
            user__email=email, token=token_request
        ).first()
        if token is None:
            raise serializers.ValidationError(
                {
                    "status": "Failure",
                    "error": "It is necessary to provide an email and a token",
                }
            )
        return token
