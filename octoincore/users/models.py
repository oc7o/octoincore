from email.policy import default

from django.contrib.auth.models import AbstractUser
from django.db import models

from octoincore.payments.models import OrderInvoice


class ExtendUser(AbstractUser):

    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    profile_image = models.ImageField(
        upload_to="uploads/profile_images/",
        blank=True,
        null=True,
        default="defaults/profile_image.png",
    )

    def products_sold_this_month_count(self):
        return OrderInvoice.objects.filter(
            order__basket__basket_objects__product_inventory__product__owner=self,
            order__created_at__month=1,
            paid=True,
        ).count()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
