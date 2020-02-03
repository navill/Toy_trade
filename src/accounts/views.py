from django.contrib.auth.views import LoginView as DefaultLoginView, LogoutView as DefaultLogoutView
from django.http import Http404
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView, UpdateView
from django.views.generic.base import View

from accounts.forms import UserProfileForm, LoginForm
from accounts.models import UserProfile

from location.signals import user_logged_in
from location.utils import get_client_ip
from notification.models import Action
from notification.utils import get_comment_action
from products.models import Comment


class Home(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'home.html')
        else:
            return redirect('login')

    def post(self, request, *args, **kwargs):
        # 알림 확인 -> 알림 지우기
        is_checked = request.POST.get('check')
        comment_actions = get_comment_action(request, comment=Comment)
        if is_checked:
            for action in comment_actions:
                action.check = True
            Action.objects.bulk_update(comment_actions, ['check'])
        return redirect('home')


class UserProfileDetailView(DetailView):
    template_name = 'accounts/profile_detail.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        # 인증 확인
        if self.request.user.is_authenticated:
            user = self.request.user
            # 접근자와 프로필 유저가 동일한지 확인
            if username == user.username:
                obj = UserProfile.objects.with_user().get(user=user)
                return obj
            raise Http404
        raise Http404

    def get(self, request, *args, **kwargs):
        # 내 게시물을 제외한 모든 게시물 등록 확인
        user = request.user
        user_profile = self.get_object()
        qs = Action.objects.all()

        # 내 게시글에 대해 누군가가 댓글 등록
        reply_qs = qs.exclude(user=user).by_model(Comment, model_queryset=True).select_related('product').filter(
            product__user=user)

        # 내 위치와 동일한 유저의 댓글
        if user_profile.filtered_city:
            replies = reply_qs.filter(city=user.userprofile.city)[:5]
        else:
            replies = reply_qs[:5]
        # 프로필 업데이트 정보
        info_qs = qs.filter(user=request.user).by_model(UserProfile)[:4]

        # 내 위치 정보
        ip = get_client_ip()
        user_session = request.session['geo_address']
        lat = user_session['lat']
        lng = user_session['long']

        coordinates = f'lat: {lat}, lng: {lng}'
        context = {
            'object': user_profile,
            'my_info': info_qs,
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
