from django.contrib import admin
from order.models import SimpleOrder, OrderStatus,SubCategory,Category

admin.site.register(SimpleOrder)
admin.site.register(OrderStatus)
admin.site.register(SubCategory)
admin.site.register(Category)