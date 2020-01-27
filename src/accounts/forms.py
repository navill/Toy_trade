from django import forms
from django.contrib.auth.forms import AuthenticationForm

from accounts.models import UserProfile


class UserProfileForm(forms.ModelForm):
    address = forms.CharField(max_length=150)
    city = forms.CharField(max_length=150)
    filtered_city = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            'address', 'city', 'filtered_city'
        ]


class LoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError('계정이 활성화 되어있지 않습니다.')
