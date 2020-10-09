from django.shortcuts import render
from .models import Item
from django.views.generic import ListView, DetailView
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
