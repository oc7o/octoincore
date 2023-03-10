import typing
from decimal import Decimal

import requests
from django.conf import settings
from requests import Session


class BTCPayClient:
    client: Session
    token: str
    btcpay_instance: str
    default_store_id: str
    default_currency: str

    def __init__(
        self,
        token: str,
        btcpay_instance: str,
        default_store_id: str,
        default_currency: str,
    ) -> None:
        self.token = token
        self.btcpay_instance = btcpay_instance
        self.default_store_id = default_store_id
        self.default_currency = default_currency
        self.client = Session()
        self.client.headers["Content-Type"] = "application/json"
        self.client.headers["Authorization"] = "token " + self.token

    def get_stores(self):
        return self.client.get(self.btcpay_instance + "/api/v1/stores").json()

    def get_store(self, storeId: str = None):
        if storeId is None:
            storeId = self.default_store_id
        return self.client.get(
            self.btcpay_instance + "/api/v1/stores/" + storeId
        ).json()

    def get_invoices(self, storeId: str = None):
        if storeId is None:
            storeId = self.default_store_id
        return self.client.get(
            self.btcpay_instance + f"/api/v1/stores/{storeId}/invoices"
        ).json()

    def get_invoice(self, invoiceId: str, storeId: str = None):
        if storeId is None:
            storeId = self.default_store_id
        return self.client.get(
            self.btcpay_instance + f"/api/v1/stores/{storeId}/invoices/{invoiceId}"
        ).json()

    def create_invoice(self, amount: Decimal, storeId: str = None):
        if storeId is None:
            storeId = self.default_store_id
        data = {
            "checkout": {
                "speedPolicy": "HighSpeed",  # "Highspeed": 0, "MediumSpeed": 1, "LowMediumSpeed": 2, "LowSpeed": 6
                "paymentMethods": ["BTC"],
                "defaultPaymentMethod": "BTC",
                "expirationMinutes": 60 * 24,
                "monitoringMinutes": 60 * 24,
                "paymentTolerance": 100,
                "redirectURL": "https://localhost:5173/checkout/done",  # TODO: https://sloow.de/
                "redirectAutomatically": True,
                "requiresRefundEmail": False,
                "defaultLanguage": "en-US",
            },
            "receipt": {"enabled": True, "showQR": None, "showPayments": None},
            "amount": amount,
            "currency": self.default_currency,
        }
        """
        # "metadata": {
        #     "orderId": "string",
        #     "orderUrl": "string"
        # },

        # "additionalSearchTerms": [
        #     "string"
        # ]
        """

        return self.client.post(
            self.btcpay_instance + f"/api/v1/stores/{storeId}/invoices", json=data
        ).json()


def get_btcpay_client():
    print(settings.BTCPAY_SERVER_URL)
    client = BTCPayClient(
        token=settings.BTCPAY_TOKEN,
        btcpay_instance=settings.BTCPAY_SERVER_URL,
        default_store_id=settings.BTCPAY_STORE_ID,
        default_currency=settings.BTCPAY_CURRENCY,
    )  # "EUR"
    return client
