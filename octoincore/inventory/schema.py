import datetime
import typing
from decimal import Decimal

import strawberry
from django.conf import settings

from octoincore.types import JSON
from octoincore.users.models import ExtendUser

from .models import (
    Brand,
    Category,
    Media,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductAttributeValues,
    ProductInventory,
    ProductType,
    Stock,
)

if typing.TYPE_CHECKING:
    from octoincore.users.schema import UserType

    from .schema import ProductType


@strawberry.django.type(model=ProductAttribute)
class ProductAttributeType:
    name: str


@strawberry.django.type(model=Brand)
class BrandType:
    name: str
    slug: str


@strawberry.django.type(model=ProductAttributeValue)
class ProductAttributeValueType:
    product_attribute: ProductAttributeType
    attribute_value: str


@strawberry.django.type(model=Media)
class MediaType:
    img_url: str


@strawberry.django.type(model=Category)
class CategoryType:
    name: str
    slug: str


@strawberry.django.type(model=ProductInventory)
class ProductInventoryType:
    sku: str
    upc: str
    is_active: bool
    is_default: bool
    retail_price: Decimal
    store_price: Decimal
    sale_price: Decimal
    brand: typing.Optional[BrandType]
    attribute_values: typing.List[ProductAttributeValueType]
    product: typing.Annotated["ProductType", "ProductType"]

    @strawberry.field
    def product_images(self, info) -> typing.List[MediaType]:
        images = []
        for media in self.media_product_inventory.all():
            images.append(
                MediaType(
                    img_url=info.context.request.build_absolute_uri(media.img_url.url)
                )
            )
        return images

    @strawberry.field
    def attributes(self, info) -> JSON:
        values = self.attribute_values.all()
        attributes = {}
        for value in values:
            attributes[value.product_attribute.name] = value.attribute_value
        return attributes


@strawberry.django.type(model=Product)
class ProductType:
    web_id: str
    slug: str
    name: str
    description: str
    category: typing.List[CategoryType]
    is_active: bool
    created_at: str
    updated_at: str
    product: typing.List[ProductInventoryType]
    owner: typing.Annotated["UserType", strawberry.lazy("octoincore.users.schema")]

    @strawberry.field
    def starting_from_price(self, info) -> Decimal:
        minimal_price = self.product.order_by("store_price").first().store_price
        return minimal_price

    @strawberry.field
    def default_image(self, info) -> typing.Optional[MediaType]:
        if self.product.first() is not None:
            if self.product.first().media_product_inventory.first() is not None:
                media = self.product.first().media_product_inventory.first()
                return MediaType(
                    img_url=info.context.request.build_absolute_uri(media.img_url.url),
                )
        return None


# def resolve_products():
#     return Product.objects.all()


@strawberry.type
class InventoryQuery:
    # products: typing.List[ProductType] = strawberry.django.field()

    @strawberry.field
    def products(self, info: strawberry.types.Info) -> typing.List[ProductType]:
        return Product.objects.all()

    @strawberry.field
    def product_by_web_id(
        self, info: strawberry.types.Info, web_id: str
    ) -> typing.Optional[ProductType]:
        try:
            return Product.objects.get(web_id=web_id)
        except Product.DoesNotExist:
            return None

    @strawberry.field
    def product_inventory_by_sku(
        self, info: strawberry.types.Info, sku: str
    ) -> typing.Optional[ProductInventoryType]:
        try:
            return ProductInventory.objects.get(sku=sku)
        except ProductInventory.DoesNotExist:
            return None

    @strawberry.field
    def product_inventories_by_skus(
        self, info: strawberry.types.Info, skus: typing.List[str]
    ) -> typing.List[ProductInventoryType]:
        return ProductInventory.objects.filter(sku__in=skus)
