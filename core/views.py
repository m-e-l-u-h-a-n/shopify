from django.shortcuts import render
from .models import Item
# Create your views here.


def item_list(req):
    context = {
        "items": Item.objects.all()
    }
    return render(req, "home-page.html", context=context)


def products(req):
    return render(req, "product-page.html", context={})


def checkout(req):
    return render(req, "checkout-page.html", context={})
