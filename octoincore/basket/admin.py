from django.contrib import admin

from .models import Basket, BasketObject

admin.site.register(Basket)
admin.site.register(BasketObject)
