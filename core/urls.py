from django.urls import path
from .views import HomeView, item_detail_view, CheckoutView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_from_cart, PaymentView, AddCouponView, RequestRefundView, ProfileView


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('product/<slug>/', item_detail_view, name="product"),
    path('add-coupon/', AddCouponView.as_view(), name="add-coupon"),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path('remove-single-item-from-cart/<slug>/',
         remove_single_from_cart, name='remove-single-item-from-cart'),
    path('payment/<payment_options>', PaymentView.as_view(), name="payment"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('request-refund/', RequestRefundView.as_view(), name="request-refund")
]
