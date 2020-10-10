from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Order, OrderItem
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.utils import timezone
# Create your views here.


class HomeView(ListView):
    """Home view is  used for listing of all the Items present for selling in the website."""
    model = Item
    paginate_by = 10
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
            messages.success(req, "Item suuccessfully added to the cart.")
        else:
            messages.success(req, "Item suuccessfully added to the cart.")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=req.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(req, "Item suuccessfully added to the cart.")
    return redirect("product", slug=slug)


def remove_from_cart(req, slug):
    """
        Handles the logic of removal from the cart.
        If an order of the user is already pending then remove the selected item from that order if it is in the order.
    """
    item = get_object_or_404(Item, slug=slug)
    order_queryset = Order.objects.filter(user=req.user, is_ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        # if item already exists in the order.
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=req.user, is_ordered=False)[0]
            order.items.remove(order_item)
            order.save()
            messages.success(req, "Item successfully removed from the cart.")
        else:
            # add a message the no such item exists in the order.
            messages.info(req, "This item is not is the cart.")
            return redirect("product", slug=slug)
    else:
        # add a message saying user does not have a order.
        messages.info(req, "You don't have any active orders.")
        print("User currently has no orders.")
        return redirect("product", slug=slug)
    return redirect("product", slug=slug)
