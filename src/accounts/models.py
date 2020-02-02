from django.contrib.auth import get_user_model
from django.db import models

from location.naver_geolocation import get_address
from location.signals import user_logged_in
from location.utils import get_client_ip

User = get_user_model()


class UserProfileManager(models.Manager):
    def with_user(self):
        return self.select_related('user')

    def all(self):
        return super(UserProfileManager, self).all()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    filtered_city = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    geo_address = models.TextField(blank=True, null=True)

    objects = UserProfileManager()

    def __str__(self):
        return str(self.user)


# 유저 로그인 시 signal(signals.py:user_logged_in(request))
def user_logged_in_receiver(sender, request, *args, **kwargs):
    user = request.user
    ip_address = get_client_ip()
    session = request.session
    if ip_address:
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        try:
            geo_address = get_address(ip_address)
            # city = str(city_data['r2']) + ' ' + str(city_data['r3'])
            city = str(geo_address['r3'])
            user_profile.city = city
            user_profile.geo_address = geo_address
            session['city'] = city
            session['geo_address'] = geo_address
            session['ip_address'] = ip_address
            
            user_profile.save()
        except:
            user_profile.city_data = '주소를 알 수 없습니다.'
            user_profile.city = '주소를 알 수 없습니다.'
            user_profile.save()


user_logged_in.connect(user_logged_in_receiver)
