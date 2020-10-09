from django.contrib import admin

# register your models here.
from .models import *

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
