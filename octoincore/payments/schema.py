import datetime
import typing
import uuid

import strawberry
from django.conf import settings

from octoincore.basket.models import Basket
from octoincore.basket.schema import BasketType
from octoincore.captcha.models import Captcha
from octoincore.inventory.models import ProductInventory
from octoincore.inventory.schema import ProductInventoryType
from octoincore.types import JSON

# from .utils import create_btcpay_client, get_btcpay_client
from .btcpayserver_client import get_btcpay_client
from .models import Order, OrderInvoice

# @strawberry.type
# class OrderProductInventoryType:
#     # order: "OrderType"
#     product_inventory: ProductInventoryType
#     quantity: int


# @strawberry.type
# class OrderInvoiceType:
#     # order: "OrderType"
#     invoice_id: str
#     invoice_url: str
#     price: float
#     created_at: datetime.datetime
#     expired_at: datetime.datetime


# @strawberry.django.type(model=Order)
# class OrderType:
#     id: int
#     invoices: typing.List[OrderInvoiceType]
#     order_product_inventories: typing.List[OrderProductInventoryType]

#     @strawberry.field
#     def total_price(self, info) -> float:
#         total_price = 0
#         for invoice in self.invoices.all():
#             total_price += invoice.price
#         return total_price

#     @strawberry.field
#     def total_quantity(self, info) -> int:
#         total_quantity = 0
#         for product_inventory in self.order_product_inventories.all():
#             total_quantity += product_inventory.quantity
#         return total_quantity


@strawberry.django.type(model=OrderInvoice)
class OrderInvoiceType:
    invoice_id: str
    invoice_url: str
    price: float
    created_at: datetime.datetime
    expired_at: datetime.datetime


@strawberry.django.type(model=Order)
class OrderType:
    firstname: str
    lastname: str
    email: str
    street: str
    city: str
    zip_code: str
    status: str

    basket: BasketType
    invoice: OrderInvoiceType


@strawberry.type
class PaymentsQuery:
    # @strawberry.field
    # def btcpay_client_host(self, info) -> str:
    #     return get_btcpay_client().host

    @strawberry.field
    def invoices(self, info) -> typing.List[JSON]:
        return get_btcpay_client().get_invoices()

    @strawberry.field
    def check_order(self, info, code: str) -> OrderType:
        return Order.objects.get(code=code)

    # @strawberry.field
    # def rates(self, info) -> typing.List[str]:
    #     return get_btcpay_client().get_rate("USD")


@strawberry.type
class PaymentsMutation:
    # @strawberry.mutation
    # def setup_btcpay_client(self, code: str, host: str) -> bool:
    #     create_btcpay_client(code, host)
    #     return True

    # @strawberry.mutation
    # def create_order(self, info, cart: JSON) -> OrderType:
    #     order = Order.objects.create()
    #     total_sum = 0
    #     for item in cart:
    #         product_inventory = ProductInventory.objects.get(sku=item)
    #         total_sum += product_inventory.store_price * cart[item]
    #         OrderProductInventory.objects.create(
    #             order=order, product_inventory=product_inventory, quantity=cart[item],
    #         )
    #     order_invoice = get_btcpay_client().create_invoice(amount=float(total_sum))
    #     order.invoices.create(
    #         invoice_id=order_invoice["id"],
    #         invoice_url=order_invoice["checkoutLink"],
    #         price=order_invoice["price"],
    #     )

    #     return order

    @strawberry.mutation
    def create_order(
        self,
        info,
        basket_web_id: str,
        firstname: str,
        lastname: str,
        city: str,
        street: str,
        zip_code: str,
        email: str,
        captcha_web_id: str,
        captcha_text: str,
    ) -> OrderType:

        captcha = Captcha.objects.get(web_id=captcha_web_id)
        if captcha.captcha != captcha_text:
            captcha.delete()
            raise Exception("Captcha is not valid")
        captcha.delete()

        basket = Basket.objects.get(web_id=basket_web_id)

        order = Order()
        order.order_key = uuid.uuid4()[:12]
        order.firstnmae = firstname
        order.lastname = lastname
        order.city = city
        order.street = street
        order.zip_code = zip_code
        order.email = email
        order.basket = basket
        order.save()

        basket.locked = True

        order_invoice = get_btcpay_client().create_invoice(
            amount=float(basket.total_price())
        )
        print("order_invoice", order_invoice)

        invoice = OrderInvoice()
        invoice.order = order
        invoice.invoice_id = order_invoice["id"]
        invoice.invoice_url = order_invoice["checkoutLink"]
        invoice.price = order_invoice["amount"]
        invoice.save()

        print("invoice", invoice)

        return order
