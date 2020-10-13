from django.urls import path
from .views import HomeView, ItemDetailView, CheckoutView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_from_cart


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('product/<slug>/', ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    path('remove-single-item-from-cart/<slug>/',
         remove_single_from_cart, name='remove-single-item-from-cart')
]
