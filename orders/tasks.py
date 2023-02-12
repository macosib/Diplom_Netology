from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task()
def new_order(order, user):
    send_mail(
        subject="Order status",
        message=f"Order created - order number: {order.id}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )
