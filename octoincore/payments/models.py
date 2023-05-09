from django.db import models

from octoincore.basket.models import Basket
from octoincore.models import OctoModel


class Order(OctoModel):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)

    status = models.CharField(
        max_length=255,
        default="new",
        choices=[
            ("unknown", "unknown"),
            ("new", "new"),
            ("paid", "paid"),
            ("shipped", "shipped"),
            ("canceled", "canceled"),
        ],
    )

    basket = models.OneToOneField(
        Basket, on_delete=models.CASCADE, related_name="order"
    )

    def __str__(self):
        return f"{self.status} - {self.code}"


class OrderInvoice(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="invoice"
    )
    invoice_id = models.CharField(max_length=255)
    invoice_url = models.URLField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
