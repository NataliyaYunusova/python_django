from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import Group

from .models import Product, Order
from django.utils.translation import gettext_lazy as _


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"
        labels = {
            'name': _('Название'),
            'price': _('Цена'),
            'description': _('Описание'),
            'discount': _('Скидка'),
            'preview': _('Превью')
        }

    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "delivery_address", "promocode", "user", "products"


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = "name",
