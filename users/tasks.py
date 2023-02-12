from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from users.models import ConfirmEmailToken, User


@shared_task()
def new_user_registered(user):
    """Отправка письма с подтверждением регистрации"""

    token, _ = ConfirmEmailToken.objects.get_or_create(user=user)

    send_mail(
        subject="Complete registration",
        message=f"Token to complete registration - {token.key}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )
