from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(min_length=1)
    apartment_address = forms.CharField(required=False, min_length=1)
    country = CountryField(blank_label="Select country").formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    zip = forms.CharField(min_length=5)
    same_shipping_address = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(
        widget=forms.CheckboxInput(), required=False)
    payment_options = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
