from datetime import datetime

from django import forms
from main.models import *


class ProductForm(forms.ModelForm):
    created = forms.DateTimeField(initial=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), required=False)

    class Meta:
        model = Product
        exclude = ('user',)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)
