from django.contrib.auth.views import LoginView as DefaultLoginView, LogoutView as DefaultLogoutView
from django.http import Http404
from django.shortcuts import render, redirect, resolve_url

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.base import View

from accounts.forms import UserProfileForm, LoginForm
from accounts.models import UserProfile

from location.signals import user_logged_in


class Home(View):
    def get(self, request):
        if request.user.is_authenticated:
            print(True)
            return render(request, 'home.html')
        else:
            return redirect('account_login')


class UserProfileDetailView(DetailView):
    template_name = 'accounts/profile_detail.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        # 인증 확인
        if self.request.user.is_authenticated:
            user = self.request.user
            # 접근자와 프로필 유저가 동일한지 확인
            if username == user.username:
                # qs = UserProfile.objects.filter(user=user).user()
                obj, created = UserProfile.objects.user().get_or_create(user=user)
                return obj
            raise Http404
        raise Http404


class LoginView(DefaultLoginView):
    form_class = LoginForm
    template_name = 'account/login.html'

    def form_valid(self, form):
        form_ = super().form_valid(form)
        # if self.request.user.is_authenticated:
        #     user_logged_in.send(self.request.user, request=self.request)
        return form_


class LogoutView(DefaultLogoutView):
    pass


class UserProfileUpdateView(UpdateView):
    template_name = 'accounts/profile_update.html'
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')

        print(username)
        # 인증 확인
        if self.request.user.is_authenticated:
            user = self.request.user
            # 접근자와 프로필 유저가 동일한지 확인
            if username == user.username:
                qs = UserProfile.objects.filter(user=user)
                if qs.exists():
                    obj = qs.first()
                    return obj
                else:
                    raise Http404
        raise Http404

    def get_success_url(self):
        user = self.request.user
        return reverse("accounts:detail", kwargs={'username': user})
