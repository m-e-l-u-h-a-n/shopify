from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from .models import BillingAddress
# Create your views here.


class HomeView(ListView):
    """Home view is  used for listing of all the Items present for selling in the website."""
    model = Item
    paginate_by = 10
    template_name = "home.html"


class ItemDetailView(DetailView):
    """A view to deal with the display details of a particular item in the cart."""
    model = Item
    template_name = 'product.html'


class OrderSummaryView(LoginRequiredMixin, View):
    """
        Returns an order with all it's details.
    """

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {
                "order": order
            }
            return render(self.request, 'order-summary.html', context=context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any actiive orders.")
            return redirect('/')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            "form": form
        }
        return render(self.request, "checkout.html", context=context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality for these fields.
                # same_billing_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_options = form.cleaned_data.get('payment_options')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                # TODO: add redirect to the selected payment options.
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                messages.success("Successfully placed the order.")
                return redirect('checkout')
            messages.warning(self.request, "Failed Checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any actiive orders.")
            return redirect('checkout')
        return redirect('checkout')


@login_required
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
            messages.success(req, "Item successfully added to the cart.")
        else:
            messages.success(req, "Item successfully added to the cart.")
            order_item.quantity = 1
            order_item.save()
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=req.user, ordered_date=ordered_date)
        order_item.quantity = 1
        order_item.save()
        order.items.add(order_item)
        messages.success(req, "Item successfully added to the cart.")
    return redirect("order-summary")


@login_required
def remove_from_cart(req, slug):
    """
        Handles the logic of removal from the cart.
        `It completly removes the item from the cart.`
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
            order_item.quantity = 0
            order_item.save()
            order.items.remove(order_item)
            order.save()
            messages.success(req, "Item successfully removed from the cart.")
            return redirect("order-summary")
        else:
            # add a message the no such item exists in the order.
            messages.info(req, "This item is not is the cart.")
            return redirect("product", slug=slug)
    else:
        # add a message saying user does not have a order.
        messages.info(req, "You don't have any active orders.")
        print("User currently has no orders.")
        return redirect("product", slug=slug)


@login_required
def remove_single_from_cart(req, slug):
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                messages.success(req, "Quantity updated successfully.")
                order_item.save()
            else:
                order.items.remove(order_item)
                order.save()
                print("Item removed form the cart")
                messages.success(req, "Item removed from the cart.")
            return redirect('order-summary')
        else:
            # add a message the no such item exists in the order.
            messages.info(req, "This item is not is the cart.")
            print("This item is not is the cart.")
            return redirect("order-summary")
    else:
        # add a message saying user does not have a order.
        messages.info(req, "You don't have any active orders.")
        print("User currently has no orders.")
        return redirect("order-summary")
