from django.db import models

from octoincore.models import OctoModel


class BasketObject(OctoModel):
    """
    BasketObject model
    """

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

    def __str__(self):
        return f"{self.product_inventory.product.name} - {self.quantity}"

    def __unicode__(self):
        return self.basket_object_id

    class Meta:
        db_table = "basket_object"
        verbose_name = "BasketObject"
        verbose_name_plural = "BasketObjects"


class Basket(OctoModel):
    """
    Basket model
    """

    locked = models.BooleanField(default=False)

    @property
    def total_price(self):
        total = 0
        for basket_object in self.basket_objects.all():
            total += (
                basket_object.product_inventory.store_price * basket_object.quantity
            )
        return total

    @property
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
