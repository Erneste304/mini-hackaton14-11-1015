from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter detailed product description...'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter product name...'
            }),
            'price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'min': '0'
            })
        }
        labels = {
            'name': 'Product Name',
            'description': 'Product Description',
            'price': 'Price ($)',
            'stock': 'Stock Quantity',
            'image': 'Product Image'
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name.strip()) < 3:
            raise forms.ValidationError("Product name must be at least 3 characters long.")
        return name.strip()