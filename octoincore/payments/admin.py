from django.contrib import admin

from .models import Order, OrderInvoice


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderInvoice)
