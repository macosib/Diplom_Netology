from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator

USER_TYPE_CHOICES = (
    ("shop", "Магазин"),
    ("buyer", "Покупатель"),
)


class UserManager(BaseUserManager):
    """
    Класс для управления пользователями
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создание нового пользователя по email и password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """

    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = "email"

    email = models.EmailField(_("email address"), unique=True)
    company = models.CharField(verbose_name="Компания", max_length=60, blank=True)
    position = models.CharField(verbose_name="Должность", max_length=60, blank=True)
    type = models.CharField(
        verbose_name="Тип пользователя",
        choices=USER_TYPE_CHOICES,
        max_length=5,
        default="buyer",
    )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "User list"
        ordering = ("email",)


class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="contacts",
        blank=True,
        on_delete=models.CASCADE,
    )

    city = models.CharField(max_length=50, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house = models.CharField(max_length=15, verbose_name="Дом", blank=True)
    structure = models.CharField(max_length=15, verbose_name="Корпус", blank=True)
    building = models.CharField(max_length=15, verbose_name="Строение", blank=True)
    apartment = models.CharField(max_length=15, verbose_name="Квартира", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f"{self.city} {self.street} {self.house}"


class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="confirm_email_tokens",
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("When was this token generated")
    )

    token = models.CharField(_("Token"), max_length=64, db_index=True, unique=True)

    class Meta:
        verbose_name = "Токен подтверждения Email"
        verbose_name_plural = "Токены подтверждения Email"

    @staticmethod
    def generate_key():
        """generates a pseudo random code using os.urandom and binascii.hexlify"""
        return get_token_generator().generate_token()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
