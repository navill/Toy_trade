from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from config import settings

User = get_user_model()


class UserProfileManager(models.Manager):
    def user(self):
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

