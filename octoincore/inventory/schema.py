import datetime
import typing
import uuid
from decimal import Decimal

import strawberry
from django.conf import settings
from django.contrib.auth import get_user_model
from strawberry.file_uploads import Upload

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
)
from .models import ProductType as ProductTypeModel
from .models import Stock

if typing.TYPE_CHECKING:
    from octoincore.users.schema import UserType

    from .schema import ProductType


GenericType = typing.TypeVar("GenericType")


@strawberry.type
class PaginationWindow(typing.List[GenericType]):
    items: typing.List[GenericType] = strawberry.field(
        description="The list of items in this pagination window."
    )

    total_items_count: int = strawberry.field(
        description="Total number of items in the filtered dataset."
    )


def get_pagination_window(
    dataset: typing.List[GenericType],
    ItemType: type,
    limit: int,
    offset: int = 0,
    filters: dict[str, str] = {},
) -> PaginationWindow:
    """
    Get one pagination window on the given dataset for the given limit
    and offset, ordered by the given attribute and filtered using the
    given filters
    """

    if limit <= 0 or limit > 100:
        raise Exception(f"limit ({limit}) must be between 0-100")

    # TODO: replace with django-filters
    # if filters:
    #     dataset = list(filter(lambda x: matches(x, filters), dataset))
    if "user" in filters.keys():
        dataset = dataset.filter(owner__username=filters["user"])

    if "search" in filters.keys():
        dataset = dataset.filter(name__icontains=filters["search"])

    if "is_active" in filters.keys():
        dataset = dataset.filter(is_active=filters["is_active"])

    if offset != 0 and not 0 <= offset < len(dataset):
        raise Exception(f"offset ({offset}) is out of range " f"(0-{len(dataset) - 1})")

    total_items_count = len(dataset)

    items = dataset[offset : offset + limit]

    return PaginationWindow(items=items, total_items_count=total_items_count)


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


@strawberry.django.type(model=ProductTypeModel)
class ProductTypeType:
    name: str


@strawberry.input
class MediaInputType:
    img_url: Upload


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
        if self.product.order_by("store_price").first() is not None:
            minimal_price = self.product.order_by("store_price").first().store_price
        else:
            minimal_price = Decimal(0)
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

    # @strawberry.field
    # def products(
    #     self,
    #     info: strawberry.types.Info,
    #     user: str | None = None,
    #     search: str | None = None,
    #     category: str | None = None,
    # ) -> typing.List[ProductType]:
    #     return Product.objects.all()

    @strawberry.field
    def products(
        self,
        info: strawberry.types.Info,
        user: str | None = None,
        search: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginationWindow[ProductType]:
        filters = {}
        if user is not None:
            filters["user"] = user
        if search is not None:
            filters["search"] = search
        if category is not None:
            filters["category"] = category
        filters["is_active"] = True

        return get_pagination_window(
            dataset=Product.objects.all(),
            ItemType=ProductType,
            limit=limit,
            offset=offset,
            filters=filters,
        )

    @strawberry.field
    def me_products(
        self,
        info: strawberry.types.Info,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginationWindow[ProductType] | None:
        if info.context.request.user.is_authenticated:
            filters = {}
            filters["user"] = info.context.request.user.username

            return get_pagination_window(
                dataset=Product.objects.all(),
                ItemType=ProductType,
                limit=limit,
                offset=offset,
                filters=filters,
            )
        raise Exception("User is not authenticated")

    @strawberry.field
    def categories(
        self,
        info: strawberry.types.Info,
    ) -> typing.List[CategoryType]:
        return Category.objects.all()

    @strawberry.field
    def product_types(
        self,
        info: strawberry.types.Info,
    ) -> typing.List[ProductTypeType]:
        return ProductTypeModel.objects.all()

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


@strawberry.type
class InventoryMutation:
    @strawberry.mutation
    def create_product(
        self,
        info: strawberry.types.Info,
        name: str,
        description: str,
        category: str,
    ) -> ProductType:
        if info.context.request.user.is_authenticated:
            product = Product.objects.create(
                name=name,
                description=description,
                is_active=False,
                web_id=uuid.uuid4().hex[:16],
                owner=info.context.request.user,
            )
            product.category.add(Category.objects.get(slug=category))
            return product
        raise Exception("User is not authenticated")

    @strawberry.mutation
    def create_product_inventory(
        self,
        info: strawberry.types.Info,
        product: str,
        store_price: Decimal,
        is_active: bool | None = False,
        is_default: bool | None = False,
        weight: Decimal | None = None,
        # retail_price: Decimal,
        # sale_price: Decimal,
        media: typing.List[MediaInputType] | None = None,
        brand: str | None = None,
        product_type: str | None = None,
        attribute_values: JSON | None = None,
    ) -> ProductInventoryType:
        if info.context.request.user.is_authenticated:
            product_inventory = ProductInventory()
            product_inventory.product = Product.objects.get(web_id=product)
            product_inventory.sku = uuid.uuid4().hex[:16]
            product_inventory.is_active = is_active
            product_inventory.is_default = is_default
            product_inventory.weight = weight
            # product_inventory.retail_price = retail_price
            product_inventory.store_price = store_price
            # product_inventory.sale_price = sale_price
            if brand is not None:
                product_inventory.brand = Brand.objects.get(slug=brand)
            if product_type is not None:
                product_inventory.product_type = ProductTypeModel.objects.get(
                    name=product_type
                )
            product_inventory.save()
            if media is not None:
                Media.objects.bulk_create(
                    [
                        Media(
                            img_url=m.img_url,
                            product_inventory=product_inventory,
                        )
                        for m in media
                    ]
                )
            # if attribute_values is not None:
            #     for attribute_value in attribute_values:
            #         ProductAttributeValue.objects.create(
            #             product_inventory=product_inventory,
            #             product_attribute=ProductAttribute.objects.get(
            #                 slug=attribute_value.product_attribute
            #             ),
            #             attribute_value=attribute_value.attribute_value,
            #         )
            return product_inventory
        raise Exception("User is not authenticated")

    @strawberry.mutation
    def delete_product_inventory(
        self,
        info: strawberry.types.Info,
        sku: str,
    ) -> bool:
        if info.context.request.user.is_authenticated:
            ProductInventory.objects.filter(sku=sku).delete()
            return True
        raise Exception("User is not authenticated")
