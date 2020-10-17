from django.contrib import admin

# register your models here.
from .models import *


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


def set_being_delivered(modeladmin, request, queryset):
    queryset.update(being_delivered=True)


def set_recieved_status(modeladmin, request, queryset):
    queryset.update(recieved=True)


make_refund_accepted.short_description = 'Update orders to refund granted'
set_being_delivered.short_description = 'Set beign delivered to True'
set_recieved_status.short_description = 'Set recieved status to True'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_ordered', 'being_delivered',
                    'recieved', 'refund_requested', 'refund_granted', 'billing_address', 'shipping_address', 'payment', 'coupon']
    list_filter = ['user', 'is_ordered', 'being_delivered',
                   'recieved', 'refund_requested', 'refund_granted']
    list_display_links = ['user', 'shipping_address',
                          'billing_address', 'payment', 'coupon']
    search_fields = [
        'user__username',
        'ref_code',
    ]
    actions = [make_refund_accepted, set_being_delivered, set_recieved_status]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = [
        'default',
        'address_type',
        'country'
    ]
    search_fields = [
        'user',
        'street_address',
        'apartment_address',
        'zip'
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
