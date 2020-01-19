from django import forms

from accounts.models import UserProfile


class UserProfileForm(forms.ModelForm):
    address = forms.CharField(max_length=150)

    class Meta:
        model = UserProfile
        fields = [
            'address'
        ]
