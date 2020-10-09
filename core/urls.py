from django.urls import path
from .views import HomeView, ItemDetailView, checkout, add_to_cart, remove_from_cart


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('checkout/', checkout, name="checkout"),
    path('product/<slug>/', ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
]
