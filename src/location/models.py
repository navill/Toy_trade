from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from location.signals import user_logged_in

User = get_user_model()


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    city_data = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.city_data:
            return str(self.city_data)
        return self.user.username


# 유저 로그인 시 signal 발생 -> session 생성
def user_logged_in_receiver(sender, request, *args, **kwargs):
    user = sender
    # ip_address
    # geo = get_client_city_data(request)

    session_key = request.session.session_key
    UserSession.objects.create(user=user, session_key=session_key)


user_logged_in.connect(user_logged_in_receiver)
