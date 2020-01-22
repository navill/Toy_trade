from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.db.models import Prefetch
from django.db.models.signals import post_save
from django.urls import reverse

from notification.utils import create_action

User = get_user_model()

BUY_OR_SELL = (
    ('buy', 'Buy'),
    ('sell', 'Sell')
)


class ProductQuerySet(models.QuerySet):
    def with_user(self):
        return self.select_related('user')


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return super(ProductManager, self).all()


def handle_upload(instance, filename):
    if instance.user:
        return f"{instance.user}/images/{filename}"
    return f"unknown/images/{filename}"


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=handle_upload, blank=True, null=True)
    type = models.CharField(choices=BUY_OR_SELL, default='sell', max_length=5)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'pk': self.id})


def post_save_product_receiver(sender, instance, created, *args, **kwargs):
    user = instance.user
    message = f'{user}가 게시물을 작성하였습니다 - {instance.title}'
    create_action(user=user, verb=message, obj=instance)


post_save.connect(post_save_product_receiver, sender=Product)


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=150)
    parent = models.ForeignKey('self', related_name='reply', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return str(self.product)


def post_save_comment_receiver(sender, instance, created, *args, **kwargs):
    user = instance.user
    message = f'{user}가 게시물{instance.product}에 대한 댓글을 작성하였습니다'
    create_action(user, message, instance)


post_save.connect(post_save_comment_receiver, sender=Comment)