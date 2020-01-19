from django import forms

from .models import Product, Comment


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title', 'price', 'description', 'image'
        ]


class CommentForm(forms.ModelForm):
    comment = forms.CharField(label='Your name', max_length=100)

    class Meta:
        model = Comment
        fields = [
            'comment'
        ]
