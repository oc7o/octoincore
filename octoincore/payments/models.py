from django.db import models

from octoincore.basket.models import Basket

# from picklefield.fields import PickledObjectField


# class BTCPayClientStore(models.Model):
#     client = PickledObjectField()


# class BTCPayBinding(models.Model):
#     token = models.CharField(max_length=255)
#     btcpay_instance: str = models.CharField(max_length=2023)
#     default_store_id: str = models.CharField(max_length=255)
#     default_currency: str = models.CharField(max_length=255)


class Order(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)

    basket = models.OneToOneField(
        Basket, on_delete=models.CASCADE, related_name="order"
    )

    created_at = models.DateTimeField(auto_now=True)
    # expired_at = models.DateTimeField()


class OrderInvoice(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="invoice"
    )
    invoice_id = models.CharField(max_length=255)
    invoice_url = models.URLField()
    # status = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    # created_at = models.DateTimeField()
    # expired_at = models.DateTimeField()
    # currency = models.CharField(max_length=255)
    # date = models.DateTimeField()
