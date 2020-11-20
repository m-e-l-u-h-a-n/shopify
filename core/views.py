from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Order, OrderItem, Address, Payment, Coupon, Refund
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RefundForm
from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchVector

# Create your views here.
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
            break
    return valid


def check_first_time(request):
    order_qs = Order.objects.filter(user=request.user, is_ordered=True)

    if len(order_qs):
        return False
    return True


class HomeView(ListView):
    """Home view is  used for listing of all the Items present for selling in the website."""
    paginate_by = 10
    template_name = "home.html"

    def get_queryset(self):
        query_term = self.request.GET.get('title', '')
        category = self.request.GET.get('category', '')
        if not category:
            if not query_term:
                queryset = Item.objects.order_by('title').all()
            else:
                vector = SearchVector('title', 'description')
                query = SearchQuery(query_term)
                queryset = Item.objects.order_by('title').annotate(
                    search=vector).filter(search=query)
        else:
            if not query_term:
                queryset = Item.objects.filter(
                    category=category).order_by('title')
            else:
                query_term = Item.objects.filter(category=category).order_by('title').annotate(
                    search=vector).filter(search=query)
        return queryset


def item_detail_view(request, slug):

    if request.method == 'GET':
        item = Item.objects.get(slug=slug)
        same_category_items = Item.objects.filter(category=item.category)
        context = {
            "item": item,
            "same_category_items": same_category_items
        }
        return render(request, 'product.html', context=context)


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
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any active orders.")
            return redirect('home')
        except TypeError:
            messages.info(
                self.request, "You need to login to access the page.")
            return redirect('account_login')
        context = {
            'form': form,
            'order': order,
            'coupon_form': CouponForm(),
            'show_coupon_form': True,
        }
        shipping_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='S',
            default=True
        )
        if shipping_address_qs.exists():
            context.update(
                {'default_shipping_address': shipping_address_qs[0]})
        billing_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='B',
            default=True
        )
        if billing_address_qs.exists():
            context.update(
                {'default_billing_address': billing_address_qs[0]})

        return render(self.request, "checkout.html", context=context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using default shipping address.")
                    shipping_address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if shipping_address_qs.exists():
                        shipping_address = shipping_address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.error(
                            self.request, "No default shipping address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new shipping address.")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    print()
                    if valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.error(
                            self.request, "Shipping address field is required")
                        return redirect('checkout')

                    set_default_shipping = form.cleaned_data.get(
                        'set_default_shipping')
                    if set_default_shipping:
                        shipping_address.default = True
                        shipping_address.save()
                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                elif use_default_billing:
                    print("Using default billing address.")
                    billing_address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if billing_address_qs.exists():
                        billing_address = billing_address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.error(
                            self.request, "No default billing address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new billing address.")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    if valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.error(
                            self.request, "Billing address field is required!")
                        return redirect('checkout')
                    set_default_billing = form.cleaned_data.get(
                        'set_default_billing')
                    if set_default_billing:
                        billing_address.default = True
                        billing_address.save()

                payment_options = form.cleaned_data.get('payment_options')
                if payment_options == 'S':
                    return redirect('payment', payment_options="stripe")
                elif payment_options == 'P':
                    return redirect('payment', payment_options="paypal")
                else:
                    messages.warning(
                        self.request, "Failed checkout(invalid payment option)!")
                    return redirect('checkout')
                messages.success("Successfully placed the order.")
                return redirect('checkout')
            else:
                print(form.errors)
                messages.warning(self.request, "Failed Checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any active orders.")
            return redirect('checkout')
        return redirect('checkout')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any active orders.")
            return redirect('home')
        context = {
            'order': order,
            'coupon_form': CouponForm(),
            'show_coupon_form': False
        }
        return render(self.request, "payment.html", context=context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        token = self.request.POST.get('stripeToken')
        print('token = ', token)
        amount = int(order.get_total())
        # TODO: check if the order is not null.
        try:
            charge = stripe.Charge.create(
                amount=amount,  # in dollars
                currency="usd",
                # TODO: check why token is not coming in self.request.POST.get('stripeToken')
                source="tok_in",
                description="My First Test Charge (created for API docs)",
            )
            payment = Payment()
            payment.stripe_charge_id = charge.id
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
            order_items = order.items.all()
            order_items.update(is_ordered=True)
            for order_item in order_items:
                order_item.save()
            order.is_ordered = True
            order.ref_code = create_ref_code()
            order.payment = payment
            order.save()
            messages.success(self.request, "Order successfully placed!")
            return redirect('checkout')
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            print(e)
            messages.error(self.request, f'${e.error.message}')
            return redirect('checkout')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            print(e)
            messages.error(self.request, "Request limit error.")
            return redirect('checkout')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.error(self.request, "Invalid parameters")
            return redirect('checkout')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            print(e)
            messages.error(self.request, "Not authentiacted")
            return redirect('checkout')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            print(e)
            messages.error(self.request, "Network error")
            return redirect('checkout')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            print(e)
            messages.error(
                self.request, "Something went wrong, no amount deducted.")
            return redirect('checkout')
        except Exception as e:
            # Send an email to yourselves
            print(e)
            messages.error(
                self.request, "Unexpected error, will be fixed soon.")
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
            messages.info(req, "This item is not in your cart.")
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


def get_coupon(request, code):
    print('code = ', code)
    try:
        coupon = get_object_or_404(Coupon, code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, "Invalid Coupon code!")
        return redirect('checkout')


class AddCouponView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            if code == 'FIRST_TIME':
                if check_first_time(self.request):
                    try:
                        order = Order.objects.get(
                            user=self.request.user, is_ordered=False)
                        order.coupon = get_coupon(self.request, code)
                        order.save()
                        messages.success(
                            self.request, "Coupon applied succesfully.")
                        return redirect('checkout')
                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "You do not have any active order.")
                        return redirect('checkout')
                else:
                    messages.warning(
                        self.request, "It's not your first order.")
                    return redirect('checkout')
            elif code == 'THREE_THOUSAND':
                try:
                    order = Order.objects.get(
                        user=self.request.user, is_ordered=False)
                    if order.coupon:
                        messages.info(self.request,
                                      "A coupon is already active for this order!")
                        return redirect('checkout')
                    if order.get_total() > 3000:
                        order.coupon = get_coupon(self.request, code)
                        order.save()
                        messages.success(
                            self.request, "Coupon applied successfully!")
                        return redirect('checkout')
                    else:
                        messages.info(self.request,
                                      "Order total should be greater than 3000 to claim it!")
                        return redirect('checkout')

                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "You do not have any active order.")
                    return redirect('checkout')
            else:
                messages.warning(
                    self.request, "Invalid coupon code requested!")
                return redirect("checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            "form": form
        }
        return render(self.request, 'request_refund.html', context=context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
            # store the refund in a model
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.success(
                    self.request, "Request submitted successfully!")
                return redirect('request-refund')
            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exists.")
                return redirect('request-refund')
