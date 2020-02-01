from PIL import Image
from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.db.models.signals import post_save, pre_save
from django.urls import reverse

from notification.utils import create_action

User = get_user_model()

BUY_OR_SELL = (
    ('buy', 'Buy'),
    ('sell', 'Sell')
)


class ProductQuerySet(models.QuerySet):
    def with_user(self):
        return self.select_related('user__userprofile')

    def with_comment(self):
        return self.prefetch_related('comment_set')


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
    city = models.CharField(max_length=20, null=True, blank=True)

    objects = ProductManager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'pk': self.id})

    def count_comment(self):
        comments = self.comment_set.all()
        return len(comments)

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     if self.id is not None:
    #         image = Image.open(self.image.path)
    #         print(image)
    #         image = image.resize((500, 350), Image.ANTIALIAS)
    #         image.save(self.image.path)


def pre_save_product_receiver(sender, instance, *args, **kwargs):
    instance.city = instance.user.userprofile.city


def post_save_product_receiver(sender, instance, created, *args, **kwargs):
    # image size 조절 
    image = Image.open(instance.image.path)
    # print(image)
    image = image.resize((500, 300), Image.ANTIALIAS)
    image.save(instance.image.path)
    
    user = instance.user
    message = f'{user}가 게시물을 작성하였습니다 - {instance.title}'
    create_action(user=user, verb=message, obj=instance)


pre_save.connect(pre_save_product_receiver, sender=Product)
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
        return str(self.id)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'pk': self.product_id})


def post_save_comment_receiver(sender, instance, created, *args, **kwargs):
    user = instance.user
    message = f'{user}가 게시물{instance.product}에 대한 댓글을 작성하였습니다'
    create_action(user, message, obj=instance, target_user=instance.product.user)


post_save.connect(post_save_comment_receiver, sender=Comment)
