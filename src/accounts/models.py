from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.db.models.signals import post_save

from config import settings
from notification.utils import create_action

User = get_user_model()


class UserProfileManager(models.Manager):
    def with_user(self):
        return self.select_related('user')

    def all(self):
        return super(UserProfileManager, self).all()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = UserProfileManager()

    def __str__(self):
        return str(self.user)


def post_save_profile_receiver(sender, instance, created, *args, **kwargs):
    user = instance.user
    message = '내 profile 이 업데이트 되었습니다.'
    create_action(user, message, instance)


post_save.connect(post_save_profile_receiver, sender=UserProfile)
