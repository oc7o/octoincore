import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from octoincore.payments.models import Order, OrderInvoice


class ExtendUser(AbstractUser):
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")
    profile_image = models.ImageField(
        upload_to="uploads/profile_images/",
        blank=True,
        null=True,
        default="defaults/profile_image.png",
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=5, default=0, verbose_name="balence"
    )

    def products_sold_this_month_count(self):
        return OrderInvoice.objects.filter(
            order__basket__basket_objects__product_inventory__product__owner=self,
            order__created_at__month=1,
            paid=True,
        ).count()

    def amount_earned_this_month(self) -> float:
        a = Order.objects.filter(
            basket__basket_objects__product_inventory__product__owner=self,
            created_at__month=datetime.datetime.now().month,
            status__in=["paid", "shipped"],
        )
        b = a.aggregate(
            models.Sum("basket__basket_objects__product_inventory__store_price")
        )

        return (
            b["basket__basket_objects__product_inventory__store_price__sum"]
            if b["basket__basket_objects__product_inventory__store_price__sum"]
            else 0
        )

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
