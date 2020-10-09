from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Order, OrderItem
from django.views.generic import ListView, DetailView
from django.utils import timezone
# Create your views here.


class HomeView(ListView):
    """Home view is  used for listing of all the Items present for selling in the website."""
    model = Item
    template_name = "home-page.html"


class ItemDetailView(DetailView):
    """A view to deal with the display details of a particular item in the cart."""
    model = Item
    template_name = 'product.html'


def checkout(req):
    return render(req, "checkout-page.html", context={})


def add_to_cart(req, slug):
    """
        Handles the logic of addition to the cart.
        If an order of the user is already pending then add the selected item to that order else add the item to the newly created order.
    """
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=req.user, is_ordered=False)
    order_queryset = Order.objects.filter(user=req.user, is_ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        # if item already exists in the order.
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=req.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect("product", slug=slug)
