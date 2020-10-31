from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
# Create your models here.


CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class Item(models.Model):
    """It represents an item on the website."""
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=15)
    label = models.CharField(choices=LABEL_CHOICES, max_length=15)
    slug = models.SlugField()
    description = models.TextField(default="No description provided")
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={"slug": self.slug})

    def get_saved_amount(self):
        return self.price - self.discount_price


class OrderItem(models.Model):
    """Just to creates a link between an order going on and actual items on the website."""
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_price(self):
        return (self.item.price * self.quantity)

    def get_total_discount_price(self):
        return (self.item.discount_price * self.quantity)

    def get_saved_amount(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        else:
            return self.get_total_price()


class Address(models.Model):
    """A model representing billing address related information for a model."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}\'s {self.apartment_address}'

    class Meta:
        verbose_name_plural = "Addresses"


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    """An Order that can be placed on the website"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    is_ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        Address, related_name="billing_address", on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(
        Address, related_name="shipping_address", on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payment,
                                on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    """
        1. Item added to the cart
        2. Adding a billing address
        (Failed Checkout)
        3. Payment
        preprocessing, processing, packaging, etc..
        4. Being delivered
        5. Recieved
        6. Refunds
    """

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def get_coupon_discount(self):
        if self.coupon:
            return ((self.get_total()) * (self.coupon.percentage)) / 100
        else:
            return 0

    def get_total_after_coupon(self):
        return self.get_total() - self.get_coupon_discount()


class Coupon(models.Model):
    """A model handling referral codes and coupons for an order."""
    code = models.CharField(max_length=15)
    percentage = models.FloatField(default=0)

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField(max_length=254)

    def __str__(self):
        return f'{self.pk}'
