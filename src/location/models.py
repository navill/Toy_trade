from django.conf import settings
from django.db import models

# Create your models here.
from .signals import user_logged_in
from .utils import get_client_city_data, get_client_ip


# User = get_user_model()


class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, null=True, blank=True)
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


# 유저 로그인 시 signal 발생 -> session 생성
def user_logged_in_receiver(sender, request, *args, **kwargs):
    user = sender
    ip_address = get_client_ip()
    city_data = None
    city = None
    if ip_address:
        try:
            city_data = get_client_city_data(ip_address)
            city = str(city_data['r2']) + ' ' + str(city_data['r3'])
        except:
            city_data = None
    request.session['city'] = city
    session_key = request.session.session_key
    print(session_key)
    # public ip-address 수집 -> citi data 수집 -> UserSession 생성
    usersession = UserSession.objects.filter(user=user, ip_address=ip_address,
                                             country=city_data['country'],
                                             city_data=city_data,
                                             city=city,
                                             )
    if len(usersession) >= 1:
        user_session = usersession.first()
        user_session.session_key = session_key
        user_session.save()
    else:
        UserSession.objects.create(user=user, ip_address=ip_address,
                                   country=city_data['country'],
                                   city_data=city_data,
                                   city=city,
                                   session_key=session_key
                                   )


user_logged_in.connect(user_logged_in_receiver)
