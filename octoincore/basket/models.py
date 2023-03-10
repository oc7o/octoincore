from django.db import models


class BasketObject(models.Model):
    """
    BasketObject model
    """

    web_id = models.CharField(max_length=255, unique=True)
    basket = models.ForeignKey(
        "basket.Basket",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="basket_objects",
    )
    product_inventory = models.ForeignKey(
        "inventory.ProductInventory",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="baskets",
    )
    quantity = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.basket_object_id

    class Meta:
        db_table = "basket_object"
        verbose_name = "BasketObject"
        verbose_name_plural = "BasketObjects"


class Basket(models.Model):
    """
    Basket model
    """

    web_id = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    locked = models.BooleanField(default=False)

    # user = models.ForeignKey(
    #     "users.User", on_delete=models.CASCADE, null=True, blank=True
    # )

    def total_price(self):
        total = 0
        for basket_object in self.basket_objects.all():
            total += (
                basket_object.product_inventory.store_price * basket_object.quantity
            )
        return total

    def total_qty(self):
        total = 0
        for basket_object in self.basket_objects.all():
            total += basket_object.quantity
        return total

    def __unicode__(self):
        return self.basket_id

    class Meta:
        db_table = "basket"
        verbose_name = "Basket"
        verbose_name_plural = "Baskets"
