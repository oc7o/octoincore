from django.contrib import admin

from .models import Order, OrderInvoice

admin.site.register(Order)
admin.site.register(OrderInvoice)
