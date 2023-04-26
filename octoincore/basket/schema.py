import typing
import uuid
from datetime import datetime
from decimal import Decimal

import strawberry

from octoincore.inventory.models import ProductInventory
from octoincore.inventory.schema import ProductInventoryType

from .models import Basket, BasketObject


@strawberry.django.type(model=BasketObject)
class BasketObjectType:
    web_id: str
    product_inventory: typing.Annotated["ProductInventoryType", "ProductInventoryType"]
    quantity: int
    created: datetime
    updated: datetime


@strawberry.django.type(model=Basket)
class BasketType:
    web_id: str
    created: datetime
    updated: datetime
    basket_objects: typing.List[
        typing.Annotated["BasketObjectType", "BasketObjectType"]
    ]
    total_price: Decimal
    total_qty: int

    @strawberry.field
    def vendor_basket_objects(self, info) -> typing.List[BasketObjectType]:
        return BasketObject.objects.filter(
            product_inventory__product__owner=info.context.request.user,
        ).all()


@strawberry.type
class BasketQuery:
    @strawberry.field
    def basket(self, info, web_id: str) -> BasketType:
        basket = Basket.objects.get(web_id=web_id)
        return basket


@strawberry.type
class BasketMutation:
    @strawberry.mutation
    def create_basket(self, info) -> BasketType:
        basket = Basket.objects.create(web_id=uuid.uuid4().hex[:8])
        return basket

    @strawberry.mutation
    def add_to_basket(
        self, info, web_id: str, product_inventory_sku: str, quantity: int
    ) -> BasketType:
        basket = Basket.objects.get(web_id=web_id)
        if basket.locked:
            raise Exception("Basket is locked")
        product_inventory = ProductInventory.objects.get(sku=product_inventory_sku)
        basket_objects = BasketObject.objects.filter(
            basket=basket, product_inventory=product_inventory
        )
        if basket_objects.exists():
            basket_object = basket_objects.first()
            basket_object.quantity += quantity
            basket_object.save()
        else:
            basket_object = BasketObject.objects.create(
                basket=basket,
                product_inventory=product_inventory,
                quantity=quantity,
                web_id=uuid.uuid4().hex[:8],
            )
        return basket

    @strawberry.mutation
    def remove_from_basket(
        self, info, web_id: str, product_inventory_sku: str
    ) -> BasketType:
        basket = Basket.objects.get(web_id=web_id)
        if basket.locked:
            raise Exception("Basket is locked")
        product_inventory = ProductInventory.objects.get(sku=product_inventory_sku)
        basket_object = BasketObject.objects.get(
            basket=basket,
            product_inventory=product_inventory,
        )
        basket_object.delete()
        return basket

    @strawberry.mutation
    def update_basket(
        self, info, web_id: str, product_inventory_id: str, quantity: int
    ) -> BasketType:
        basket = Basket.objects.get(web_id=web_id)
        if basket.locked:
            raise Exception("Basket is locked")
        product_inventory = ProductInventory.objects.get(id=product_inventory_id)
        basket_object = BasketObject.objects.get(
            basket=basket,
            product_inventory=product_inventory,
        )
        basket_object.quantity = quantity
        basket_object.save()
        return basket

    @strawberry.mutation
    def empty_basket(self, info, web_id: str) -> BasketType:
        basket = Basket.objects.get(web_id=web_id)
        if basket.locked:
            raise Exception("Basket is locked")
        basket.basket_objects.all().delete()
        return basket

    @strawberry.mutation
    def delete_basket(self, info, web_id: str) -> BasketType:
        basket = Basket.objects.get(web_id=web_id)
        if basket.locked:
            raise Exception("Basket is locked")
        basket.delete()
        return basket
