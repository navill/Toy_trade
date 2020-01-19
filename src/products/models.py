from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.urls import reverse

User = get_user_model()

BUY_OR_SELL = (
    ('buy', 'Buy'),
    ('sell', 'Sell')
)


def handle_upload(instance, filename):
    if instance.user:
        return f"{instance.user}/images/{filename}"
    return f"unknown/images/{filename}"


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=handle_upload, blank=True, null=True)
    type = models.CharField(choices=BUY_OR_SELL, default='sell', max_length=5)

    # location - session
    # from writer(session or redis)
    # sell_or_buy - choice
    # kw = array(postgresql) or json

    # price - decimal
    # description - text
    # image
    # comment - foreignkey
    # trade_method - choice
    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'pk': self.id})


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=150)
    parent = models.ForeignKey('self', related_name='reply', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.product)
