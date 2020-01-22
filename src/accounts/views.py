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
from notification.models import Action
from products.models import Product, Comment


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
                obj, created = UserProfile.objects.with_user().get_or_create(user=user)
                return obj
            raise Http404
        raise Http404

    def get(self, request, *args, **kwargs):
        # 내 게시물을 제외한 모든 게시물 등록 확인
        # actions = Action.objects.exclude(user=request.user).by_model(Product)
        # print(actions)  # -> 나를 제외한 사람들이 생성한 Product objects

        # 내 게시글에 대해 누군가가 댓글 등록
        qs = Action.objects.all()
        replies = qs.exclude(user=request.user).by_model(Comment, model_queryset=True).select_related('product')

        # 내 정보 업데이트
        my_info = qs.filter(user=request.user).by_model(UserProfile)[:4]

        # 내 위치 정보
        # {lat: -25.344, lng: 131.036};
        coordinates = '{lat: -25.344, lng: 131.036}'
        context = {
            'object': self.get_object(),
            'my_info': my_info,
            'replies': replies,
            'coordinates': coordinates,
        }
        return render(request, 'accounts/profile_detail.html', context=context)


class LoginView(DefaultLoginView):
    form_class = LoginForm
    template_name = 'account/login.html'

    def form_valid(self, form):
        form_ = super().form_valid(form)
        if self.request.user.is_authenticated:
            user_logged_in.send(self.request.user, request=self.request)
            # print(self.request.session.items())
        return form_


class LogoutView(DefaultLogoutView):
    pass


class UserProfileUpdateView(UpdateView):
    template_name = 'accounts/profile_update.html'
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
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

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save()
        return super().post(request, *args, **kwargs)
