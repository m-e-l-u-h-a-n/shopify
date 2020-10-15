from django import template

from core.models import Order
register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, is_ordered=False)
        if qs.exists():
            total_item_count = 0
            for order_item in qs[0].items.all():
                total_item_count += order_item.quantity
            return total_item_count
        else:
            return 0
    else:
        return 0
