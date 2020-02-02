from django.conf import settings
from django.db import models

# Create your models here.
from accounts.models import UserProfile
from location.naver_geolocation import get_address
from .signals import user_logged_in
from .utils import get_client_ip


# User = get_user_model()


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    city_data = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.city_data and self.country:
            return f'{self.city} - {self.country}'
        return str(self.user.username)

#
# # 유저 로그인 시 signal(signals.py:user_logged_in(request)) 발생 -> session 생성
# def user_logged_in_receiver(sender, request, *args, **kwargs):
#     user = request.user
#     ip_address = get_client_ip()
#
#     city_data = None
#     city = None
#     if ip_address:
#         try:
#             city_data = get_address(ip_address)
#             # city = str(city_data['r2']) + ' ' + str(city_data['r3'])
#             city = str(city_data['r3'])
#             user_profile, created = UserProfile.objects.get_or_create(user=user)
#             user_profile.city = city
#             user_profile.ip_address = ip_address
#             user_profile.save()
#         except:
#             # print('?')
#             city_data = '주소를 알 수 없습니다.'
#             city = '주소를 알 수 없습니다.'
#
#     # public ip-address 수집 -> city data 수집 -> UserSession 생성
#     UserSession.objects.get_or_create(user=user, ip_address=ip_address,
#                                       country=city_data['country'],
#                                       city_data=city_data,
#                                       city=city,
#                                       )
#
#
# user_logged_in.connect(user_logged_in_receiver)
