from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import DetailView, ListView
from django.views.generic.base import View

from accounts.models import UserProfile


class Home(View):
    def get(self, request):
        if request.user.is_authenticated:
            print(True)
            return render(request, 'home.html')
        else:
            return redirect('account_login')


class UserProfileDetailView(DetailView):
    template_name = 'profile_detail.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        qs = None
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
